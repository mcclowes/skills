# Organising a data-export module

Good instinct to think about structure up front. The three responsibilities you listed — CSV generation, job kick-off, status polling — map cleanly onto distinct layers, and the trick is to keep those layers separated so each file stays small, single-purpose, and easy to reason about. That's what makes it pleasant for both you and Claude: when a file does one thing, an agent can load it, understand it, and edit it without dragging in half the codebase.

## Recommended layout

Assuming App Router, I'd colocate a feature module under `src/features/data-export/` and keep the routes thin:

```
src/features/data-export/
  domain/
    types.ts              # ExportJob, ExportStatus, ExportRequest — shared shapes
    csv.ts                # pure: rows -> CSV string. No I/O, no Next, fully testable
    csv.test.ts
  jobs/
    createExportJob.ts    # persist a job record, enqueue work, return job id
    getExportJob.ts       # read job status by id
    runExportJob.ts       # the actual worker: generate CSV, store it, update status
    queue.ts              # thin adapter over your queue/cron (QStash, Inngest, etc.)
  storage/
    exportStore.ts        # where CSVs land (Blob/S3) + signed URL helpers
  api/                    # optional: server-only orchestration the routes call
    startExport.ts
    pollExport.ts
  client/
    useExportStatus.ts    # polling hook (SWR/React Query) the UI consumes
    ExportButton.tsx
    ExportButton.module.scss

src/app/api/exports/
  route.ts                # POST -> startExport()
  [id]/route.ts           # GET  -> pollExport()
```

## Why this shape

**Pure core, impure edges.** `domain/csv.ts` is the most valuable thing to isolate. CSV serialisation (escaping commas, quotes, newlines, encoding) is fiddly and exactly the kind of logic that benefits from tight unit tests. Keep it pure — rows in, string out, no database, no `fetch`, no Next imports. You can TDD it in isolation and an agent can verify a change by running one test file. Everything that touches the world (DB, queue, blob storage) lives in `jobs/` and `storage/`.

**One job, one file.** Split the job lifecycle into `createExportJob`, `getExportJob`, and `runExportJob` rather than a single `jobs.ts` god-file. They have different callers (the POST route, the GET route, the worker respectively) and different dependencies. Small files mean a smaller, more accurate context window when Claude edits one of them, and far less chance of an unrelated change sneaking in.

**Routes stay thin.** `app/api/exports/route.ts` should be a handful of lines: parse the request, call `startExport()`, map the result to a response. Don't put CSV logic or queue wiring in the route handler. This keeps the HTTP concern (validation, status codes, auth) separate from the business logic, and means the logic is reusable and testable without spinning up the route.

**A `queue.ts` seam.** Wrap whatever background mechanism you use behind one small adapter. Background jobs on Vercel usually mean an external trigger (QStash, Inngest, a cron route) rather than an in-process worker, because serverless functions don't outlive the request. Putting that behind `queue.ts` means the rest of the code says `enqueue(jobId)` and doesn't care how, so swapping providers later touches one file.

**Client polling as a hook.** Keep the polling logic in `useExportStatus.ts` (interval, backoff, stop-on-terminal-state) and let components just render. React Query / SWR with `refetchInterval` handles most of this for you; don't hand-roll a `setInterval` in a component.

## A few decisions worth making early

- **Shared types in `domain/types.ts`.** Define `ExportStatus` as a union (`'pending' | 'running' | 'complete' | 'failed'`) once and import it everywhere — server, worker, and client. This is the single most useful thing for keeping an AI agent consistent across files; it has one source of truth to anchor to.
- **Status is a state machine.** Be explicit about legal transitions (pending → running → complete/failed). It prevents a class of bugs and reads clearly.
- **Return early, store the file, hand back a URL.** The POST returns a job id immediately; the worker writes the CSV to blob storage and stamps the job with a download URL; the GET returns status plus that URL when ready. Don't stream large CSVs through the polling endpoint.

## What not to do

Don't start with one big `data-export.ts` "because it's all related." It is related, but related-by-feature is what the folder boundary is for — not what a single file is for. The moment CSV escaping, DB writes, queue calls, and a React hook share a file, every edit loads all of it and the agent has to hold unrelated concerns in mind at once. Equally, don't over-fragment on day one: you don't need a separate file per CSV column type or a five-layer abstraction. Start with the split above, and only break a file further when it actually grows past comfortably-readable (a couple hundred lines, or two clearly different responsibilities).

Net: separate the pure CSV core, give each job-lifecycle action its own file, hide the queue behind one adapter, keep routes and components thin, and centralise the types. That keeps every file small and single-purpose, which is exactly what makes the module easy for you to navigate and easy for Claude to edit without collateral damage.
