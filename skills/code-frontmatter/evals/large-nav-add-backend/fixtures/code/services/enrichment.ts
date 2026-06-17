/**
 * ---
 * purpose: Turns a validated RawEvent into a storable Event and assigns the AUTHORITATIVE server timestamp (client timestamp kept only for drift analysis); also derives geo + parsed user-agent and folds context into properties.
 * related:
 *   - ../store/store.ts - defines RawEvent (input) and Event (output, what EventStore.insert stores)
 *   - ../lib/useragent.ts - parseUserAgent produces the structured UserAgentInfo set here
 *   - ./ingestion.ts - the only caller; runs enrich() between validation and persistence
 *   - ../routes/ingest.ts - builds the RequestMeta (ip, userAgent, apiKeyId) passed into enrich()
 * ---
 */
import { randomUUID } from "node:crypto";
import type { Event, GeoInfo, RawEvent } from "../store/store";
import { parseUserAgent } from "../lib/useragent";

/**
 * Network/request metadata captured by the ingest route and handed to the
 * enrichment service. Kept separate from the RawEvent body because none of it
 * is client-supplied in the payload — it comes from the connection and headers.
 */
export interface RequestMeta {
  ip: string | null;
  userAgent: string | null;
  apiKeyId: string;
  /** Server receive time; injected so enrichment stays deterministic in tests. */
  receivedAt?: number;
}

/**
 * Pluggable geo lookup. The default is a no-op stub; production wires in a real
 * MaxMind/ipinfo client. Kept as an interface so enrichment doesn't hard-depend
 * on a network call.
 */
export interface GeoResolver {
  lookup(ip: string | null): GeoInfo | null;
}

const NULL_GEO: GeoResolver = {
  lookup: () => null,
};

/**
 * Turns a validated RawEvent into a fully-formed, storable Event.
 *
 * Key invariant: the SERVER timestamp is authoritative. Whatever the client put
 * in `timestamp` is preserved as `clientTimestamp` for drift analysis, but
 * `serverTimestamp` (the receive time) is what every query and time-bucket uses.
 * This prevents clients with bad clocks from skewing aggregates or back-dating
 * events outside the current window.
 */
export class EnrichmentService {
  constructor(private readonly geo: GeoResolver = NULL_GEO) {}

  enrich(raw: RawEvent, meta: RequestMeta): Event {
    const serverTimestamp = meta.receivedAt ?? Date.now();

    return {
      id: randomUUID(),
      type: raw.type,
      userId: raw.userId,
      // Authoritative time wins over any client-supplied timestamp.
      serverTimestamp,
      clientTimestamp: raw.timestamp ?? null,
      properties: this.mergeProperties(raw),
      ip: meta.ip,
      geo: this.geo.lookup(meta.ip),
      userAgent: parseUserAgent(meta.userAgent),
      apiKeyId: meta.apiKeyId,
    };
  }

  /**
   * Fold the client's declared context (url/referrer) into properties so it is
   * queryable alongside the rest, without letting it clobber explicit keys the
   * client already set in `properties`.
   */
  private mergeProperties(raw: RawEvent): Record<string, unknown> {
    const props: Record<string, unknown> = { ...(raw.properties ?? {}) };
    if (raw.context?.url && props.url === undefined) {
      props.url = raw.context.url;
    }
    if (raw.context?.referrer && props.referrer === undefined) {
      props.referrer = raw.context.referrer;
    }
    return props;
  }
}
