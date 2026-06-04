Good instinct to think about this up front — the layout you pick now will shape how painful every future edit is, for you and for Claude.

The key thing to design around: AI agents are reluctant to look at adjacent files. They work with what's open in front of them and make confident changes based on that. So the goal isn't "maximum separation" — it's splitting along boundaries where each file can be understood and edited without opening its siblings. A beautifully focused file that's missing context is worse than a slightly busier one that's self-sufficient.

Your module has three genuinely different kinds of work, and they split cleanly:

1. **CSV generation** — pure transformation. Rows in, string/buffer out. No side effects, no state.
2. **Job orchestration** — kicking off the background job and tracking its lifecycle.
3. **Status polling** — the client-side loop and the API surface it talks to.

## Suggested layout

```
app/
  api/
    exports/
      route.ts              # POST: start an export, returns a job id
      [jobId]/
        route.ts            # GET: status (+ download link when ready)
features/
  data-export/
    csv.ts                  # pure: data -> CSV. No deps on jobs/Next.
    csv.test.ts
    export-job.ts           # orchestration: start job, run it, persist status
    export-job.test.ts
    types.ts                # shared shapes: ExportJob, ExportStatus, ExportRequest
    use-export.ts           # client hook: start + poll, exposes status/progress
```

A few deliberate choices here, and the reasoning:

**`csv.ts` stands alone.** This is the textbook case for its own file. It's pure — input in, CSV out, no side effects — so it's self-documenting and an agent can work on it with almost no external context. Easy to test exhaustively too, which fits TDD nicely. Keep it free of any import from the job or Next layers so it never drags that context in.

**Keep each route file thin, and let the orchestration live in `export-job.ts`.** The route handlers should parse the request, call into `export-job.ts`, and shape the response. Don't scatter the job logic across the two route files — if the start logic lives in one route and the status logic in another, an agent editing one won't see the shape of the other, and the two halves only make sense together. Centralising them in `export-job.ts` means the route files stay readable and the coupled logic is in one place.

**`types.ts` is the one shared file worth having.** `ExportJob`, `ExportStatus` (the enum/union for queued → running → ready → failed), and the request/response shapes get referenced from the routes, the orchestration, and the client hook. Because every layer needs them and they're trivial to read, a single small types file is the rare cross-file dependency that pays for itself — an agent opening any one file can find the shapes in one obvious place.

**Co-locate the client polling logic in a `use-export.ts` hook — don't split start-vs-poll.** Starting an export and polling its status are one coherent client concern: the poll only makes sense in terms of the job the start call returned. Splitting them into separate files would just create two things that are each meaningless alone and double the cross-file lookups the agent won't perform. One hook, `useExport()`, that exposes `{ start, status, progress, downloadUrl }` is both the cleanest interface for your UI and the best prompt for Claude — it reads the hook at the call site and knows enough to proceed without reading its internals. That's a real abstraction doing real work, not just relocated code.

## What I'd resist

**Don't pre-split on reflex.** You don't need `csv-headers.ts`, `csv-rows.ts`, `csv-escape.ts` on day one. Let `csv.ts` grow as one coherent concern — a cohesive 150-line file beats three 50-line ones that only make sense read together. Split it only if it crosses a few hundred lines or starts covering genuinely separate formats.

**Don't separate "logic" from "rendering" in the hook.** The temptation will be a `use-export-state.ts` plus a `use-export-polling.ts`. Resist it for the same reason — they need each other to be understood. If the hook gets large, reach for a well-named internal helper function before you reach for a new file.

**Let the route handlers stay simple.** If `[jobId]/route.ts` is just "look up job, return status," that's fine — it doesn't need its own service layer. Add one only when there's real branching to hide behind an interface.

## Rule of thumb for the build-out

When a file grows, ask whether each piece can be understood in isolation. If yes, it's a fair split. If a piece only makes sense by reading its sibling, keep them together or hide the detail behind a named function/hook instead. Prefer an abstraction over a new file whenever you can — it actually reduces the context needed to work with the code, whereas a split just moves the code around.

This gives you maybe five or six files for the whole module, each editable on its own, with one obvious place for shared types. That's the sweet spot: focused enough to be high-signal prompts, self-contained enough that Claude won't break things by not looking next door.
