# Structuring the data-export module

Short version: start coarser than your instinct probably tells you. You have three genuinely distinct concerns here — CSV generation, job orchestration, and status polling — and they don't all couple the same way. Organise around what can be understood in isolation, not around a reflex to give every responsibility its own file.

Here's a layout I'd reach for:

```
data-export/
  csv.ts              // pure: rows in, CSV string/stream out
  export-job.ts       // server: enqueue, run, write status
  status.ts           // shared types + status read/transition logic
  api/
    export/route.ts   // POST -> kick off job, returns jobId
    export/[id]/route.ts  // GET -> job status
  use-export.ts       // client hook: trigger + poll, owns all client state
  ExportButton.tsx    // presentational-ish UI that calls use-export
```

Why this shape, concern by concern:

**CSV generation is the easy one — give it its own file.** It's pure: data in, CSV text out, no side effects, no awareness of jobs or HTTP. That makes it self-documenting and trivially testable, and an agent can work on it with essentially zero external context. This is the kind of split that genuinely pays off, so do it. Keep escaping/quoting/streaming logic all in here rather than scattering helpers.

**The job lifecycle is tightly coupled — co-locate it.** Enqueueing a job, running it, and writing its status are always changed together and each needs the others to make sense. Don't pre-split this into `enqueue.ts` / `runner.ts` / `writer.ts`. If you do, an agent landing in `runner.ts` won't see how status is shaped or how the job was created two files over, and it'll confidently make a change that breaks the contract. Let `export-job.ts` grow — a cohesive 150–200 line file here beats three files that are each meaningless alone. Only split when it crosses ~300 lines or genuinely splits into separate concerns.

**Put the status type and its transitions in one place.** The single highest-leverage move for this module is making the job status (`pending | running | ready | failed`, plus the row shape and any error info) a real abstraction that both the server and client import. The polling client, the runner, and the status endpoint all depend on this shape. If it lives implicitly across files, every cross-file change risks drift — and the agent won't go check. One small `status.ts` that owns the type and the legal transitions removes the lookup the agent is most likely to skip.

**The client side: prefer a hook over splitting UI from logic.** This is the spot where the old instinct ("separate logic from rendering") backfires. Triggering the export and polling for status is inherently stateful and coupled — start, poll on an interval, handle ready/failed, expose a download link. If you peel that apart from the button, you get two files that only make sense together and an agent that has to open both. Instead, push all of it into `use-export()`. Now the call site reads `const { start, status, downloadUrl } = useExport()` and the component is understandable without reading the hook's internals. That's a real abstraction reducing context, not just relocated code. The component itself can then be genuinely presentational and stand on its own.

**Route handlers stay thin.** The API routes should just translate HTTP to calls into `export-job.ts` / `status.ts`. Keep them small and don't bury business logic in them — the orchestration belongs in the module so it's testable and so the agent has one obvious place to look.

The test to apply as you go: for any file, ask *can this be understood and edited without opening its siblings?* The CSV file passes trivially. The job file passes because it's cohesive. The hook passes because it hides its own state. If you find yourself making a "dumb" render file whose props are shaped by a sibling, or splitting the runner from the status writer, that's the boundary in the wrong place — merge it back.

One caution on over-splitting: resist the urge to add `types.ts`, `constants.ts`, `utils.ts` barrels up front. Co-locate types with the code that owns them (status type excepted, since it's genuinely shared) until there's a real reason to centralise. Empty-ish utility files just add lookups without adding context.
