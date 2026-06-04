# Structuring a data-export module for you and Claude

Short version: build it as a **self-contained feature module** with a clear seam between transport (routes), orchestration (services), and pure logic (CSV generation, job lifecycle). Co-locate everything for one feature in one folder, keep files small and single-purpose, and make the pure logic genuinely pure so it's trivial to test and reason about. That layout helps a human navigate and gives Claude small, well-named files it can load and edit without dragging in the whole app.

## Recommended layout

Assuming App Router:

```
src/features/data-export/
  README.md                      # 10-line orientation: what this does, the flow, where to start
  index.ts                       # public surface — what the rest of the app may import

  api/                           # transport layer (thin)
    export.routes.ts             # request parsing + response shaping, no business logic
  # (the actual route files live under app/, see below — these are the handlers they call)

  services/                      # orchestration — the "verbs"
    create-export.ts             # validate input -> enqueue job -> return job id
    get-export-status.ts         # look up job -> map to status DTO
    process-export.ts            # the worker body: load data -> generate CSV -> store -> mark done

  csv/                           # pure CSV generation, no I/O
    generate-csv.ts              # rows -> CSV string/stream
    escape.ts                    # field escaping/quoting rules
    columns.ts                   # column definitions per export type

  jobs/                          # background-job concerns
    queue.ts                     # adapter over your queue (Inngest/QStash/BullMQ/etc.)
    job-store.ts                 # persistence for job status/progress/result location
    job-status.ts                # the JobStatus state machine + transitions

  types.ts                       # shared types: ExportRequest, JobStatus, ExportResult
  errors.ts                      # typed errors (ValidationError, JobNotFoundError, ...)

  __tests__/
    generate-csv.test.ts
    job-status.test.ts
    create-export.test.ts
```

Route files stay where the framework expects them, but kept thin and delegating into the feature:

```
src/app/api/exports/route.ts            # POST -> createExport(), maybe GET list
src/app/api/exports/[id]/route.ts       # GET -> getExportStatus()
src/app/api/exports/[id]/download/route.ts   # GET -> stream the finished CSV
```

Each route handler is ~10 lines: parse, call a service, shape the response.

## The reasoning

**Feature-first, not layer-first.** Don't scatter this across top-level `services/`, `lib/`, `utils/` folders shared with the rest of the app. Keeping `data-export/` as one directory means everything related is one `ls` away, and when you tell Claude "work in the data-export module" it has a tight, complete context window instead of hunting across the tree. It also makes the feature deletable/movable as a unit.

**Three honest layers.** The recurring failure mode in export code is business logic leaking into route handlers, which makes it untestable and forces Claude to load Next.js request plumbing just to change escaping rules. So:

- **Routes** know about HTTP and nothing else.
- **Services** orchestrate — they're where the "create / status / process" verbs live and where side effects are sequenced.
- **csv/** and **job-status.ts** are pure: data in, data out, no fetch, no DB, no `Request`. This is the part with the most edge cases (escaping commas/quotes/newlines/BOM for Excel, big rows), so making it pure means you can unit-test it exhaustively and Claude can edit it with zero risk of touching infrastructure.

**Split the job concerns from the CSV concerns.** Generating a CSV and managing a background job are unrelated axes that change for different reasons. Keeping `csv/` and `jobs/` separate stops the file that knows about queues from also knowing about quoting rules. The worker (`process-export.ts`) is the one place they meet.

**Wrap the queue behind an adapter (`jobs/queue.ts`).** You haven't picked a background mechanism, and on Vercel the realistic options (Inngest, QStash, Trigger.dev, a cron + DB-polled worker) all differ. Putting one thin adapter in front means the rest of the module depends on `enqueue(job)` / `getJob(id)` and you can swap the provider later without touching services or routes. This is also the seam where serverless reality bites — long CSV generation can exceed function timeouts, so the "background job" must run somewhere that isn't the request handler.

**A `JobStatus` state machine is worth its own file.** Status polling is the heart of the UX. Model it explicitly: `queued -> processing -> completed | failed`, with the allowed transitions in one place (`job-status.ts`). The polling endpoint then just reads and maps. This prevents the classic bug where status is set ad hoc from five different spots.

## File-size and naming guidance (helps Claude specifically)

- **One concept per file, named as the thing it does.** `generate-csv.ts`, `create-export.ts`. A file Claude can identify from its name alone is one it can edit without reading three others first.
- **Keep files small** — roughly under ~200 lines. When a file does one thing, Claude can load it, change it, and you can review the diff in isolation. Giant "manager" files are where AI edits go wrong.
- **`index.ts` as the public contract.** Export only what other parts of the app should use (`createExport`, `getExportStatus`, types). Everything else stays module-private. This stops Claude (and humans) from reaching into internals and creating accidental coupling.
- **`types.ts` and `errors.ts` shared within the module** so request/status/result shapes have one definition and typed errors map cleanly to HTTP codes in the route layer.
- **A short `README.md` in the folder.** Five to ten lines: the flow (`POST /exports -> job -> poll /exports/:id -> download`), and "start in `services/` to follow the logic." This is cheap and dramatically improves how well Claude orients on the first prompt.

## What I'd push back on

Don't over-build the seams on day one. You don't need a repository abstraction, a DI container, or a generic "export engine" before you've shipped one CSV. Start with the folders above but let `jobs/queue.ts` wrap whatever concrete provider you pick, and only generalise `columns.ts` into a registry once you have a second export type. The structure above is the skeleton; resist filling it with interfaces that have exactly one implementation.

## Suggested build order (TDD-friendly)

1. `types.ts` + `csv/generate-csv.ts` with a thorough escaping test — pure, fast, no infra.
2. `jobs/job-status.ts` state machine + tests.
3. `services/create-export.ts` and `get-export-status.ts` against an in-memory `job-store.ts`.
4. Wire the real queue adapter and `process-export.ts` worker.
5. Thin route handlers last, since by then they're just glue.

That order means the risky, edge-case-heavy logic is locked down by tests before any serverless/queue complexity enters the picture.
