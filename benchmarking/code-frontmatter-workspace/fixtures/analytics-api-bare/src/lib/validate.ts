import { EVENT_TYPES, type EventType, type RawEvent } from "../store/store";

/**
 * Raised when an incoming payload fails validation. Carries a machine-readable
 * `field` and `code` so the ingest route can build a structured 400 body.
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    readonly field: string,
    readonly code: ValidationCode,
  ) {
    super(message);
    this.name = "ValidationError";
  }
}

export type ValidationCode =
  | "missing"
  | "wrong_type"
  | "unknown_enum"
  | "too_long"
  | "out_of_range"
  | "malformed";

/** Reject absurd clock skew. Clients may be a little off; days off is a bug. */
const MAX_FUTURE_SKEW_MS = 5 * 60 * 1000; // 5 minutes
const MAX_PAST_AGE_MS = 30 * 24 * 60 * 60 * 1000; // 30 days
const MAX_USER_ID_LEN = 256;
const MAX_PROPERTIES_BYTES = 32 * 1024; // 32 KiB serialized

function isPlainObject(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

function assertEventType(value: unknown): asserts value is EventType {
  if (typeof value !== "string") {
    throw new ValidationError("`type` must be a string", "type", "wrong_type");
  }
  if (!EVENT_TYPES.includes(value as EventType)) {
    throw new ValidationError(
      `unknown event type "${value}"; expected one of ${EVENT_TYPES.join(", ")}`,
      "type",
      "unknown_enum",
    );
  }
}

/**
 * Validate and normalise an untrusted request body into a RawEvent.
 *
 * This is purely structural/semantic validation of client input. It does NOT
 * assign the server timestamp or any derived fields — that happens later in the
 * enrichment step. Timestamp checks here only guard against nonsense values.
 *
 * @throws ValidationError on the first problem encountered.
 */
export function validateRawEvent(
  body: unknown,
  now: number = Date.now(),
): RawEvent {
  if (!isPlainObject(body)) {
    throw new ValidationError(
      "request body must be a JSON object",
      "$",
      "malformed",
    );
  }

  assertEventType(body.type);

  if (typeof body.userId !== "string" || body.userId.length === 0) {
    throw new ValidationError(
      "`userId` is required and must be a non-empty string",
      "userId",
      body.userId === undefined ? "missing" : "wrong_type",
    );
  }
  if (body.userId.length > MAX_USER_ID_LEN) {
    throw new ValidationError(
      `\`userId\` exceeds ${MAX_USER_ID_LEN} chars`,
      "userId",
      "too_long",
    );
  }

  let timestamp: number | undefined;
  if (body.timestamp !== undefined) {
    if (typeof body.timestamp !== "number" || !Number.isFinite(body.timestamp)) {
      throw new ValidationError(
        "`timestamp` must be a finite epoch-millis number",
        "timestamp",
        "wrong_type",
      );
    }
    if (body.timestamp > now + MAX_FUTURE_SKEW_MS) {
      throw new ValidationError(
        "`timestamp` is too far in the future",
        "timestamp",
        "out_of_range",
      );
    }
    if (body.timestamp < now - MAX_PAST_AGE_MS) {
      throw new ValidationError(
        "`timestamp` is older than the 30-day retention window",
        "timestamp",
        "out_of_range",
      );
    }
    timestamp = body.timestamp;
  }

  let properties: Record<string, unknown> | undefined;
  if (body.properties !== undefined) {
    if (!isPlainObject(body.properties)) {
      throw new ValidationError(
        "`properties` must be an object",
        "properties",
        "wrong_type",
      );
    }
    const size = Buffer.byteLength(JSON.stringify(body.properties), "utf8");
    if (size > MAX_PROPERTIES_BYTES) {
      throw new ValidationError(
        `\`properties\` exceeds ${MAX_PROPERTIES_BYTES} bytes`,
        "properties",
        "too_long",
      );
    }
    properties = body.properties;
  }

  let context: RawEvent["context"];
  if (body.context !== undefined) {
    if (!isPlainObject(body.context)) {
      throw new ValidationError(
        "`context` must be an object",
        "context",
        "wrong_type",
      );
    }
    context = {
      url: typeof body.context.url === "string" ? body.context.url : undefined,
      referrer:
        typeof body.context.referrer === "string"
          ? body.context.referrer
          : undefined,
    };
  }

  return {
    type: body.type,
    userId: body.userId,
    timestamp,
    properties,
    context,
  };
}
