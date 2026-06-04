# Organising a data-export module in Next.js

Good instinct to think about structure up front. The three responsibilities you named — CSV generation, job kick-off, status polling — map cleanly onto a layered module. The key idea: keep a thin HTTP/UI surface, put the real work in framework-agnostic logic, and isolate side effects (the job runner, storage) behind small interfaces. That separation is what makes the module pleasant for both you and Claude to work in, because each file has one job and a name that tells you what's inside.

## Recommended layout

```
src/
  features/
    export/
      index.ts                 # public surface: what the rest of the app imports
      types.ts                 # ExportJob, ExportStatus, ExportRequest, row/column types
      csv/
        generate-csv.ts        # pure: rows -> CSV string/stream
        columns.ts             # column definitions, formatting, escaping
        generate-csv.test.ts
      jobs/
        create-export-job.ts   # validate input, persist job record, enqueue
        run-export-job.ts       # the worker body: fetch data -> CSV -> upload -> mark done
        job-store.ts            # read/write job state (DB or KV) behind one interface
        queue.ts                # enqueue/handler wiring for your background runner
        create-export-job.test.ts
        run-export-job.test.ts
      status/
        get-export-status.ts    # read a job's current status + result URL
        get-export-status.test.ts
      app/                      # Next.js wiring — thin adapters only
        routes.ts               # request parsing + response shaping helpers
```

Then the route handlers stay tiny and live where Next.js expects them:

```
app/api/exports/route.ts             # POST -> createExportJob, returns { jobId }
app/api/exports/[id]/route.ts        # GET  -> getExportStatus
```

If your background job runs as its own endpoint (e.g. a Vercel cron or queue webhook hitting an API route), add `app/api/exports/[id]/run/route.ts` that simply calls `runExportJob`.

## Why this shape

**One concern per file, descriptive names.** `generate-csv.ts`, `create-export-job.ts`, `get-export-status.ts` — you (and Claude) can find the right file from the name alone, without opening it. This matters more than depth of nesting. When Claude is asked to "fix the CSV escaping," it greps `csv/`, opens one small file, and edits it without dragging the job runner or route handlers into context. Smaller, focused files mean smaller, safer diffs and fewer accidental changes to unrelated code.

**Pure core, effectful edges.** `generate-csv.ts` and `columns.ts` should take data in and return a string/stream out — no DB, no fetch, no Next.js. That makes them trivial to unit test (which suits your TDD preference) and means an agent can reason about them in isolation. All the messy parts — persistence, queueing, uploading — sit behind `job-store.ts` and `queue.ts`, so swapping your background runner (Inngest, Trigger.dev, BullMQ, a plain Vercel cron) later touches one or two files, not the whole module.

**The route handlers are adapters, not logic.** Keep `route.ts` files to: parse/validate the request, call one function from the module, shape the response. If a handler grows past ~30 lines, the logic belongs in `jobs/` or `status/`. This keeps your business logic testable without spinning up the Next.js request lifecycle, and it keeps the HTTP contract easy to read.

**A single public entry point.** `index.ts` re-exports the handful of functions the rest of the app is allowed to use (`createExportJob`, `getExportStatus`, the public types). Everything else is an internal detail. This gives both you and an agent a clear "front door" and stops the rest of the codebase reaching into internals you might refactor.

## A few specifics worth deciding early

- **Put the types in one `types.ts` and import them everywhere.** A shared `ExportStatus` union (`'pending' | 'running' | 'ready' | 'failed'`) used by the job runner, the status endpoint, and the polling client is the single most useful thing for keeping the module coherent. Claude leans heavily on these shared types to stay consistent across files.
- **Stream the CSV rather than building one giant string** if exports can be large — have `generate-csv.ts` return an async iterable / `ReadableStream`. Worth designing for now even if you start with strings, because retrofitting streaming later is painful.
- **Don't store the CSV in your job record.** Write it to blob storage (Vercel Blob, S3) and keep only a URL + status in the job row. Keeps the status table small and the polling response cheap.
- **Co-locate tests** (`*.test.ts` next to the file). It keeps the unit-under-test and its spec in the same folder, which is both your stated preference and genuinely helpful for an agent — it sees the contract and the implementation together.

## What I'd push back on

Don't reach for this many folders if the module is genuinely small. If CSV generation is one function, job handling is one function, and status is a one-line DB read, then a flat `features/export/` with four or five files (`types.ts`, `generate-csv.ts`, `create-export-job.ts`, `get-export-status.ts`, plus tests) is better than the nested version above. Folders earn their keep when a concern has several files; until then they're just clicks. Start flat, and split a folder out the moment one concern grows past two or three files. The layering principle (pure core, effectful edges, thin routes) matters at any size — the folder depth is the part you scale up only when you need it.
