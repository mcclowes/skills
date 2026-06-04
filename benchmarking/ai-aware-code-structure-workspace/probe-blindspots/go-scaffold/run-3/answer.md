# Start coarser

Start coarser. The pre-split habit made sense when humans were the only readers, but with an AI agent doing most edits it works against you, and Go's own conventions don't reward it either.

## Why the reflex hurts here

The five-file scaffold (`handler.go`, `service.go`, `repository.go`, `types.go`, `errors.go`) is layer-based, not feature-based. Every meaningful change to one payment behaviour touches all five: the handler signature, the service logic, the repo query, the struct in `types.go`, the sentinel error in `errors.go`. That's the worst possible shape for an agent.

The thing to design around is that AI tools are remarkably reluctant to read adjacent files. They work with what's open and make confident changes that break because they never checked how a type was shaped or what error was already defined two files over. Your layout maximises exactly those skipped lookups:

- A `Payment` struct in `types.go` is meaningless on its own. The agent editing `service.go` needs it but won't reliably open `types.go` to get it. So it reinvents fields, mistypes them, or invents a parallel struct.
- `errors.go` as a bucket is the classic miss. The agent adds a new `errors.New("payment not found")` inline because it never saw you already had `ErrPaymentNotFound`. Now you have two.
- `repository.go` split from `service.go` before either exists means neither file stands alone, and you've doubled the cross-file context the agent has to assemble.

You'd be paying the full cost of separation (cross-file lookups the agent skips) before you have any code to justify it.

## What to do instead

**Start with one file: `payments.go`.** Let it hold the handler, service, repo, types, and errors together while the package is small. A cohesive 200-line file the agent can edit from a complete picture beats five 40-line files that are each meaningless alone. Go is comfortable with this — a package is the real unit, and one file per package is idiomatic for small packages.

**Split when a real boundary appears, by reason, not reflex:**

- **Past ~300 lines and still climbing** — signal-to-noise is now the actual problem, so split.
- **A genuinely self-contained piece emerges** — the test is "can this be understood in isolation?" A pure mapping function, a value type with its own validation, an external client wrapper: these stand alone and earn their own file because the agent can work on them with almost no external context.
- **A second clear feature shows up** — prefer splitting by feature (`refunds.go`, `payouts.go`), each carrying its own handler-to-storage slice, over splitting by layer. Feature files keep the things-that-change-together together.

**Reach for an interface before a new file.** This is where Go helps you. A `Repository` interface defined right next to the service that consumes it is a real abstraction: the agent reads the interface at the call site and knows enough to proceed without opening the implementation. That actually reduces the context needed, where a bare file split only relocates code. Define the interface where it's used (consumer-side, Go style); the concrete Postgres or Stripe implementation can move to its own file once it's substantial, because by then it stands alone behind that interface.

## Where pre-splitting is still fine

If a file is self-contained from line one, splitting it out early costs nothing. A `client.go` wrapping an external payment provider, or a `money.go` value type with its own arithmetic and validation, are understandable in isolation — break those out whenever you like. The advice is specifically against the *layered* scaffold (`handler`/`service`/`repository`/`types`/`errors`), where every file leans on the others for meaning.

## Bottom line

Drop the up-front five-way split. Begin with `payments.go`, keep tightly coupled code together so the agent always has the full picture, and split later along boundaries where each side genuinely stands alone — feature seams and self-contained types, not layer labels. Use interfaces to cut context, not just file count. You can always split a coherent file later; un-splitting five anaemic files the agent has already filled with duplicated structs and errors is the harder cleanup.

One caveat worth naming: this is a trade-off for today's tools, not a law. As agents get better at navigating across files the threshold drifts back toward aggressive separation. Structure for the tools you have now.
