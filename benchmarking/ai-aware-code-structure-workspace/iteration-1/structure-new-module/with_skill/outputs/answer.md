Good instinct to think about this up front. The key thing to optimise for — for both you and Claude — is that **each file can be understood and edited without needing to open three siblings first**. AI agents are surprisingly reluctant to go read adjacent files; they make confident edits based on what's in front of them. So the layout that works best is one where boundaries fall on genuine "can this be understood in isolation?" lines, not on a reflex to split everything tiny.

Let me push back on one likely instinct before giving you a structure: don't pre-split this into a dozen 30-line files just because there are three "phases" (CSV, job, polling). Those three things are tightly coupled — the job kicks off CSV generation, the poller reports on the job. If you shred them across many files, you mostly create cross-file lookups that neither you nor Claude will reliably perform. Start coarser than feels natural and let files grow to a few hundred lines while they stay coherent.

## Suggested structure

```
src/features/data-export/
  index.ts                  # public surface: re-export what the rest of the app uses
  types.ts                  # shared types: ExportJob, ExportStatus, ExportRequest
  csv.ts                    # CSV generation: data in → CSV string/stream out
  export-job.ts             # job lifecycle: create, run, persist status
  use-export.ts             # client hook: kick off + poll, exposes {start, status, error}
  api/
    route.ts                # POST: start export   GET: read status (Next.js route handler)
```

If your app uses the App Router, the `api/` part may instead live at `app/api/export/route.ts` — keep the *logic* in the feature folder and let the route handler be a thin adapter that calls into `export-job.ts`. That keeps the framework boundary thin and the testable core in one place.

## Why this split and not a finer one

**`csv.ts` stands alone — separate it.** CSV generation is pure: rows in, CSV out, no side effects. That's exactly the kind of unit that's self-documenting and that Claude can work on with almost no surrounding context. It earns its own file. It's also the part most likely to grow (column formatting, escaping, streaming large datasets), so giving it room now is right.

**`export-job.ts` keeps creation, running, and status together.** Resist splitting "create the job" / "run the job" / "update status" into separate files. They share the same state shape and are always changed together — that's the textbook case for co-location. One cohesive ~150–250 line file here is better than four files that are each meaningless alone. Split it later *only* if it crosses ~300 lines or starts covering genuinely separate concerns (e.g. a storage adapter that's reused elsewhere).

**`use-export.ts` co-locates kick-off and polling.** The natural temptation is `use-start-export.ts` + `use-poll-status.ts`. Don't — they share the job ID and status state, and understanding one requires the other. One hook that exposes `{ start, status, progress, error }` is both a cleaner interface for your components *and* a complete picture for the agent. The component reads `useExport()` at the call site and knows enough to proceed without reading the internals — that's a real abstraction reducing context, which beats relocating code into more files.

**`types.ts` is the one shared file everything reads.** This is deliberate. The shape of `ExportJob` / `ExportStatus` is the thing most likely to be referenced from a file the agent is editing without it opening the definition. Keeping types in one obvious, conventionally-named place makes that lookup cheap when it does happen. Keep it small — just the shared contracts.

**`index.ts` defines the public surface** so the rest of the app (and Claude, when working elsewhere) imports from `@/features/data-export` and doesn't reach into internals. This is what lets you reorganise the insides later without a ripple.

## The rule of thumb to keep applying

As you build, when a file grows, ask **"can each half be understood on its own?"** before splitting:

- Yes (like CSV formatting peeling off into its own concern) → split, and make each side self-contained.
- No (the logic and the thing it operates on need each other) → keep them together, and if it's readability you're after, reach for a well-named function or hook *inside* the file rather than a new file.

Prefer extracting an abstraction (a named function/hook with a clear interface) over extracting a file. A new file just relocates code; a good abstraction actually shrinks the context needed to work with it.

## Tests

Put tests alongside each unit — `csv.test.ts` next to `csv.ts`, etc. Co-located tests are the cheapest possible context for an agent editing that file: it sees the contract and the implementation together.

Net: three real files for the three real concerns (CSV / job / client hook), a shared types file, a thin route adapter, and a public `index.ts` — coarser than the old "one file per responsibility" reflex, but each piece self-sufficient. Start here and split further only when a file crosses ~300 lines or genuinely splits into independent concerns.
