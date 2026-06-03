# Organising a data-export module

Good instinct to think about structure up front. The key idea: split by responsibility, not by "everything in one big file." You've actually named three distinct concerns already — CSV generation, job orchestration, and status polling — and that maps cleanly onto a folder layout. Keeping each piece small and single-purpose is exactly what makes it easy for both you and Claude to work in: small files mean focused reads, obvious places to add things, and tests that pin behaviour.

Here's a layout I'd reach for in a Next.js App Router project.

## Suggested structure

```
src/
  features/
    data-export/
      index.ts                  # public surface of the module (barrel)
      types.ts                  # shared types: ExportJob, ExportStatus, ExportRequest

      csv/
        generate-csv.ts         # pure: rows -> CSV string/stream
        generate-csv.test.ts
        serializers.ts          # field formatting, escaping, header mapping

      jobs/
        create-export-job.ts    # kicks off the background job
        run-export-job.ts       # the actual work the worker runs
        job-store.ts            # persistence (DB/queue) read+write
        job-store.test.ts

      status/
        get-job-status.ts       # read-side: look up status by id
        poll-status.ts          # client-side polling hook/util

      api/                      # thin glue to your transport layer
        export.handlers.ts      # request -> service call -> response

  app/
    api/
      export/
        route.ts                # POST: start an export  -> create-export-job
      export/[jobId]/status/
        route.ts                # GET: status -> get-job-status

  components/
    export/
      ExportButton.tsx
      ExportStatusIndicator.tsx  # consumes poll-status
```

## Why this shape

**Feature folder, not type-first.** Everything for data-export lives under `features/data-export`. You're not hunting across `lib/`, `utils/`, `services/` to change one feature. When you (or Claude) open that folder, the whole module is in view.

**Sub-folders by responsibility.** `csv/`, `jobs/`, `status/` are your three concerns. Each is independently understandable and testable. The CSV generation in particular should be *pure* — rows in, string/stream out, no DB or job knowledge — which makes it trivial to unit test and reuse.

**Thin route handlers.** The files under `app/api/.../route.ts` should do almost nothing: parse/validate the request, call into the feature module, shape the response. All real logic lives in the feature folder. This keeps your business logic free of framework coupling and easy to test without spinning up Next.

**A single public surface (`index.ts`).** Re-export only what the rest of the app should touch (e.g. `createExportJob`, `getJobStatus`, types). Internals stay internal. This gives Claude a clear "front door" and discourages deep imports into the guts of the module.

**Tests alongside implementation.** `generate-csv.test.ts` next to `generate-csv.ts`. Easy to find, and a strong signal of intended behaviour when either of us is reading the code.

## On the background job

The "kick off a job + poll for status" pattern needs three pieces wired together, and it's worth being explicit about them so the seams are clean:

1. **Enqueue** (`create-export-job`) — writes a job record (status `pending`) and pushes work onto whatever runs it.
2. **Worker** (`run-export-job`) — picks up the job, does the export, updates status (`running` -> `complete`/`failed`), stores the result location.
3. **Status read** (`get-job-status`) — a cheap lookup the client polls.

What "the worker" is depends on your deploy target — Vercel serverless functions time out, so a long CSV export usually wants a queue (Inngest, QStash, a cron-triggered worker, or a proper queue/DB). I'd keep `run-export-job` agnostic of *what* triggers it: it takes a `jobId`, does the work, updates the store. The trigger mechanism stays in one swappable place. That way if you start on `setTimeout`/a Vercel function and later move to Inngest, only the enqueue glue changes.

## A few small things that pay off

- **Co-locate the polling logic with a custom hook** (`usePollExportStatus`) so components stay dumb. The hook owns the interval, backoff, and stop-on-terminal-state logic.
- **Define the status state machine once** in `types.ts` (`'pending' | 'running' | 'complete' | 'failed'`) and reuse it everywhere. Stringly-typed status across files is a common source of drift.
- **Keep a short `README.md` or top-of-`index.ts` comment** describing the flow (enqueue -> worker -> poll). One paragraph. It's the single most useful thing for orienting Claude in a fresh session — it can read that instead of reverse-engineering the data flow from five files.

## One thing I'd push back on

Don't over-build the folder tree on day one. If `csv/` is going to be a single 60-line file, it can just be `csv.ts` until it grows. The responsibility *boundaries* above are what matter; the exact nesting can stay flat until a file gets uncomfortable to scan (say, past ~200 lines or doing two clearly different jobs). Start with the seams, split when there's real pressure to.

Want me to scaffold this out with the types, empty function stubs, and the two route handlers wired up so you've got a working skeleton to fill in?
