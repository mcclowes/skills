# Organising the data-export module

Good news: this module has clean, natural seams, so you can structure it in a way that reads well for you and for Claude at the same time. The trick is to split along boundaries where each file stands on its own, and resist the old reflex of carving everything into tiny files.

The starting question for each piece isn't "is this a separate concern?" — it's "can this be understood in isolation?" That single test does most of the work here.

## Recommended layout

```
src/features/data-export/
  csv.ts              # pure: rows in → CSV string out
  csv.test.ts
  export-job.ts       # job orchestration: start, status, the actual export work
  export-job.test.ts
  types.ts            # shared types: ExportJob, ExportStatus, etc.
  api/                # route handlers (or app/api/export/... if you prefer)
    start.ts
    status.ts
  useExportPoller.ts  # client hook: kick off + poll, exposes status/progress
```

The reasoning, piece by piece:

### CSV generation → its own file (`csv.ts`)

This is the textbook case for separation. CSV serialisation is pure: data in, string out, no side effects, no dependency on the rest of the module. Claude can open this file and fully understand it with zero external context, and it's trivially unit-testable. Keep it standalone.

### Job orchestration → keep it together (`export-job.ts`)

This is the part I'd push back on splitting prematurely. The "kick off a job" and "check its status" logic are tightly coupled — they share the job record shape, the status enum, the storage/queue mechanism, and they change together. If you split "start" and "poll" into separate files, each one only makes sense by reading the other, and Claude tends not to go open the sibling. You'd get two files that are each meaningless alone, plus a cross-file lookup the agent will skip and then get wrong.

So co-locate the job lifecycle in one file. Let it grow — a cohesive 150-to-250-line `export-job.ts` that holds the whole lifecycle is a *better* file to hand an agent than three fragments. Only split when it crosses ~300 lines or starts covering genuinely separate concerns (e.g. if the queue/storage adapter grows its own surface, pull that out behind a named interface).

Note that `csv.ts` gets *called by* `export-job.ts` but isn't coupled to it — the export job depends on the CSV module's interface, not its internals. That's a real abstraction, which is exactly the kind of boundary worth having.

### Polling on the client → a named hook (`useExportPoller`)

For the React side, reach for an abstraction rather than file structure. A `useExportPoller(jobId)` hook that returns `{ status, progress, downloadUrl, error }` means your component reads the call site and knows everything it needs without opening the hook's internals. That's strictly better than splitting polling logic into a loose helper file, because the hook has a real interface that hides its implementation.

### Types → shared file (`types.ts`)

`ExportJob`, `ExportStatus`, the request/response shapes — these are referenced from the API handlers, the job module, and the hook. One small `types.ts` they all import keeps the shapes in one obvious place. This is the one acceptable "referenced everywhere" file, because types are cheap to read and having a single source of truth prevents the API handler and the hook from drifting.

### API routes → thin handlers

Keep `start.ts` and `status.ts` thin — parse the request, call into `export-job.ts`, shape the response. The handlers stay readable on their own precisely because the real work lives behind the job module's interface.

## What I'd avoid

- **Don't pre-split the job module** into `start-job.ts` / `poll-job.ts` / `complete-job.ts`. They share too much context; you'll create files that can't be understood without each other.
- **Don't separate "logic" from "rendering"** on the client just for tidiness. If a component is genuinely smart (effects, state, the poll loop), peeling its logic into a sibling file leaves two halves that each need the other. The hook handles this cleanly instead — wrap the logic in `useExportPoller` and let the component stay presentational.
- **Don't reflexively keep every file under a screenful.** That rule was calibrated for human scrolling. Cohesion beats line count here.

## The test to apply as you go

For any file you're tempted to create: could Claude open just that file and edit it correctly without reading its siblings? `csv.ts` passes easily. A split-out `poll-job.ts` would fail. When a piece fails the test, co-locate it or hide it behind a named interface (hook/function/module) instead of relocating it into another loose file.

This is tuned to how today's agents behave — they're reluctant to go read adjacent files, so the win is keeping coupled things together and exposing real interfaces. As the tooling improves you can drift back toward finer-grained splits, but this layout will serve you well right now.
