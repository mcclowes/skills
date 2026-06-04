/**
 * ---
 * purpose: Write-path service — the one place a raw payload becomes a stored event via validate -> enrich -> persist; batch ingest allows partial success so one bad event can't drop the rest.
 * related:
 *   - ../lib/validate.ts - step 1, validateRawEvent does the structural/semantic checks and throws ValidationError
 *   - ./enrichment.ts - step 2, EnrichmentService.enrich adds derived fields + the authoritative server timestamp
 *   - ../store/store.ts - step 3, persists through EventStore.insert/insertBatch (backend-agnostic)
 *   - ../routes/ingest.ts - thin HTTP handlers that build RequestMeta and call this service
 * ---
 */
import type { Event, EventStore } from "../store/store";
import { validateRawEvent, ValidationError } from "../lib/validate";
import { EnrichmentService, type RequestMeta } from "./enrichment";

/**
 * Result of accepting a single event. `eventId` is the server-assigned id the
 * client can use for de-duplication / support.
 */
export interface IngestResult {
  eventId: string;
  serverTimestamp: number;
}

/** Summary of a batch ingest: per-item outcomes plus rolled-up counts. */
export interface BatchIngestResult {
  accepted: number;
  rejected: number;
  results: Array<
    | { ok: true; eventId: string }
    | { ok: false; field: string; code: string; message: string }
  >;
}

/**
 * IngestionService is THE place an incoming event becomes a stored event.
 *
 * Pipeline, in order:
 *   1. validate   — structural/semantic checks (lib/validate)
 *   2. enrich     — derived fields + authoritative server timestamp (enrichment)
 *   3. persist    — EventStore.insert against the configured backend
 *
 * The service is backend-agnostic: it only knows the EventStore interface, so
 * the same logic runs against Postgres, ClickHouse or memory.
 */
export class IngestionService {
  constructor(
    private readonly store: EventStore,
    private readonly enrichment: EnrichmentService,
  ) {}

  /**
   * Validate, enrich and persist a single raw payload.
   * @throws ValidationError if the payload is malformed (route maps to 400).
   */
  async ingest(body: unknown, meta: RequestMeta): Promise<IngestResult> {
    const raw = validateRawEvent(body);
    const event = this.enrichment.enrich(raw, meta);
    await this.store.insert(event);
    return {
      eventId: event.id,
      serverTimestamp: event.serverTimestamp,
    };
  }

  /**
   * Validate/enrich a batch, then persist all the events that passed in one
   * store call. Invalid items are reported but do NOT fail the whole batch —
   * partial success is intentional so one bad event can't drop 999 good ones.
   */
  async ingestBatch(
    bodies: unknown[],
    meta: RequestMeta,
  ): Promise<BatchIngestResult> {
    const enriched: Event[] = [];
    const results: BatchIngestResult["results"] = [];

    for (const body of bodies) {
      try {
        const raw = validateRawEvent(body);
        const event = this.enrichment.enrich(raw, meta);
        enriched.push(event);
        results.push({ ok: true, eventId: event.id });
      } catch (err) {
        if (err instanceof ValidationError) {
          results.push({
            ok: false,
            field: err.field,
            code: err.code,
            message: err.message,
          });
        } else {
          throw err;
        }
      }
    }

    if (enriched.length > 0) {
      await this.store.insertBatch(enriched);
    }

    return {
      accepted: enriched.length,
      rejected: results.length - enriched.length,
      results,
    };
  }
}
