# Start coarser

Short answer: drop the pre-split habit for a new package. Start with fewer, fatter files and let boundaries emerge as the code earns them. The reflex to scatter `handler.go`/`service.go`/`repository.go`/`types.go`/`errors.go` on day one is calibrated for a world where humans are the only readers, and it actively works against an AI agent.

## Why the habit hurts here

When most edits go through an agent, the binding constraint is that agents are reluctant to look at sibling files. They work with what's in front of them and make confident changes against a partial picture. A pre-split skeleton is the worst case for that: a request type lives in `types.go`, the error it returns is in `errors.go`, the function shaping it is in `service.go`, and the agent editing `handler.go` never opens the other three. You get changes that compile against the open file and break on the parts it didn't read.

Pre-splitting before there's much code makes this worse in a specific way: the splits are speculative. You're guessing at boundaries before you know where the seams actually are. Half of them will be wrong, and wrong boundaries force exactly the cross-file lookups the agent skips.

Worth noting: Go specifically doesn't reward the split. The whole package shares one namespace — there's no import or visibility cost to having `Service`, its repository, and its types in one file. `handler.go` calling something in `service.go` looks identical whether they're one file or five. So the split buys you nothing structurally; it only changes which bytes sit next to which, and that's the one thing that matters for the agent.

## What to do instead

**Start with one file, maybe two.** A new `payments` package can happily live in `payments.go` until it has real shape. Let it grow. A cohesive 200-line file that keeps the handler, the service call it wraps, and the types they pass beats four 50-line files that are each meaningless alone. Agents handle a few hundred lines fine — the human "fits on a screen" rule isn't the constraint here.

**Split on the test "can this be understood in isolation?"** — not "is this a separate concern?" Layer names like handler/service/repository are concerns, but a handler that can't be understood without its service and types isn't isolated; splitting it just doubles the lookups the agent won't do. The pieces that *do* pass the test are the ones to separate:

- **The repository / data-access layer** is often a genuinely clean seam — a narrow interface (`Store` with `Get`, `Save`) whose implementation the rest of the package never needs to read. That's a real abstraction, not just relocated code, so pulling it into `repository.go` (or behind an interface) earns its keep. The caller reads the interface and proceeds.
- **`errors.go`** is fine *once you have a meaningful set* of sentinel errors and error types. Sentinel errors are genuinely standalone — `var ErrInsufficientFunds = ...` needs no surrounding context. But there's no value creating the file to hold two errors; let them sit next to the code that returns them until there are enough to be worth gathering.

**Prefer an interface to a file split.** This is the Go-native version of "reach for an abstraction before a new file." When the data layer earns a boundary, the win is the `Store` interface, not the fact that its implementation moved files. The interface is what lets the agent work against the call site without reading the implementation. A file split with no interface just moves bytes.

## Concretely

For a brand-new payments package:

1. Start in `payments.go` (handler + service logic + the types they share). Let it reach a few hundred lines.
2. Pull out `repository.go` (or a `Store` interface) as soon as data access is real — it's the cleanest standalone seam and the one most worth isolating.
3. Add `errors.go` when you have a *set* of sentinel errors worth collecting, not before.
4. Split further only when the file crosses ~300 lines or stops being one coherent concern — and split for *that* reason, on a boundary where each resulting file stands on its own, not by reflex onto the layer-name template.

The layered file layout is a fine *destination* for a mature package. It's a bad *starting point*, because day-one splits are guesses, and wrong guesses cost the agent the context it's least likely to go find.

One caveat: if your team has a strong shared convention that every package looks the same, there's a real human-coordination value in the consistency that can outweigh this — but that's a team-norms decision, not something the code itself is asking for. Absent that, start coarse.
