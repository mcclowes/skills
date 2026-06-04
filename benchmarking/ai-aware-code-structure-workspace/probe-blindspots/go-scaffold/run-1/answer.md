# Start coarser

Drop the pre-split habit for a new package. Splitting `handler.go` / `service.go` / `repository.go` / `types.go` / `errors.go` before there's much code is laying down a five-file skeleton based on what the code is *about* to become, not what it is. That's exactly the structure that hurts an AI agent.

## Why the habit costs you with an agent

The thing to design around: agents are very reluctant to look at files other than the one in front of them. A human flips between `service.go` and `repository.go` and `types.go` without thinking. An agent tends to work from the open file and make confident edits that break because it never checked how a type was shaped two files over.

When a 60-line package is spread across five near-empty files, almost every real change forces a cross-file lookup the agent won't reliably do:

- It's editing `service.go`, but the `Payment` struct lives in `types.go` and the sentinel errors live in `errors.go`.
- It needs the repository's method signature, which is in `repository.go`.
- Each file is individually too thin to be meaningful, and the package only makes sense if you've read all five.

You've optimised the layout for a codebase that doesn't exist yet, and paid for it with cross-file context the agent skips.

The deeper point: the split here is by *layer* (handler/service/repo), but early on those layers are tightly coupled and change together. The test that matters isn't "is this a separate concern?" — it's **"can this be understood in isolation?"** A near-empty `repository.go` can't; you have to read `types.go` to know what it stores and `service.go` to know who calls it. That's the wrong boundary.

## What to do instead

**Start with one `payments.go`.** Let the handler, service, repository, types, and errors live together while the package is small and they change as a unit. A cohesive 200-ish-line file that holds the whole picture is a far better prompt than five files that are each meaningless alone. Agents handle a few hundred lines comfortably — the old "if it doesn't fit on a screen, split it" rule was calibrated for human scrolling, not for this.

**Split when a part earns it, not on a schedule.** The signals to actually break a file out:

- It crosses roughly 300–500 lines and signal-to-noise starts dropping.
- A genuine seam appears — e.g. the repository now has a real, stable interface (`type Store interface { ... }`) that callers use without caring about the implementation. That's a true abstraction, not just relocated code, and it's a good split because each side now stands on its own.
- A piece has become self-contained: types with no behaviour, or pure helpers that take inputs and return outputs with no reach into the rest of the package. Those read fine in isolation and are cheap to lift out.

**Prefer an interface over a file move.** When the repository wants to be separate, the win is the `Store` interface, not the filename. The agent reads the interface at the call site and knows enough to proceed without opening the implementation. Splitting a file only relocates code; an abstraction actually reduces the context needed to work with it.

## Go-specific notes

- This cuts against the common Go-by-layer convention, but Go doesn't care how many files a package spans — the package is the unit, files are free. So starting in one file costs you nothing structurally and you split later with a trivial cut-and-paste, no import churn (same package).
- `errors.go` is the weakest reason to pre-split. A handful of `var ErrInsufficientFunds = errors.New(...)` lines are tiny and most useful sitting next to the code that returns them. Pull them out only once there are enough to form their own coherent block.
- `types.go` is also weak early — your structs are most legible next to the methods that operate on them. A standalone types file is one of the most common "the agent edits the method but never opens the struct" traps.
- Keep `_test.go` files split per Go convention; that's orthogonal and fine.

## Bottom line

For a brand-new package, default to coarse: one file (or two — implementation + test) until the code tells you where the seams are. Reach for an interface before a new file. When you do split, the test is whether each resulting file can be understood and edited without opening the others — if not, the boundary is wrong. The five-file scaffold is a fine *destination* for a mature package; it's a poor *starting point*, and doubly so when an agent does most of the editing.

(One caveat: if your service has strong, enforced conventions — a generator, a lint rule, or a team norm that every package ships those exact five files — consistency across the codebase may be worth more than the per-package optimum. Weigh that. But if the layout is just personal habit, start coarser.)
