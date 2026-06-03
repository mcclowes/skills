/**
 * ---
 * purpose: HTTP entry point - POST /shorten creates a link, GET /:slug 302-redirects
 * related:
 *   - ./shortener.ts - core shorten/resolve logic
 *   - ./store-redis.ts - backing store wired in here
 *   - ./config.ts - listen port
 * ---
 */
import { createServer, IncomingMessage, ServerResponse } from "http";
import { Shortener } from "./shortener";
import { RedisStore } from "./store-redis";
import { getConfig } from "./config";

// In a real app this would be a configured redis client; omitted for the fixture.
declare const redisClient: any;

const shortener = new Shortener(RedisStore.fromConfig(redisClient));

async function handle(req: IncomingMessage, res: ServerResponse): Promise<void> {
  if (req.method === "POST" && req.url === "/shorten") {
    const body = await readBody(req);
    try {
      const link = await shortener.shorten(JSON.parse(body).url);
      send(res, 201, link);
    } catch (err) {
      send(res, 400, { error: (err as Error).message });
    }
    return;
  }
  if (req.method === "GET" && req.url && req.url.length > 1) {
    const slug = req.url.slice(1);
    const target = await shortener.resolve(slug);
    if (target) {
      res.writeHead(302, { Location: target });
      res.end();
    } else {
      send(res, 404, { error: "unknown slug" });
    }
    return;
  }
  send(res, 404, { error: "not found" });
}

function send(res: ServerResponse, status: number, body: unknown): void {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(body));
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve) => {
    let data = "";
    req.on("data", (chunk) => (data += chunk));
    req.on("end", () => resolve(data));
  });
}

createServer(handle).listen(getConfig().port);
