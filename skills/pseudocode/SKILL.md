---
name: pseudocode
description: Use before implementing any non-trivial logic — algorithms with subtle invariants, state machines, parsers/evaluators, numerical or financial formulas, concurrency, or anything where correct-looking code is routinely subtly wrong. Write a short language-agnostic plan (data shapes + invariants, control flow, edge cases, interface contract) and check it before generating code. Triggers on "implement this algorithm", "write a function that…", "build a parser/state machine/scheduler", "compute this formula", reworking tricky logic, or any coding task where the hard part is getting the logic right rather than wiring things together. Skip it for CRUD, glue, config, and plumbing where the code is already the spec. Apply this whenever the expensive risk is a logic bug — an off-by-one, a missed null, a wrong ordering, a broken invariant — not just when the user says "pseudocode".
license: MIT
metadata:
  author: mcclowes
  version: "0.1.0"
---

# Pseudocode

Write the *shape* of the solution before paying for the details. For logic-heavy work, a short language-agnostic plan — data shapes and their invariants, control flow, edge cases, the interface contract — catches the expensive bugs while they are still cheap to fix, and gives you (and a reviewer) a dense, glance-able artifact to check the logic against before any code exists.

## Why this exists

Generating code is now nearly free; **verifying it is the bottleneck.** The expensive bugs don't live in syntax — the compiler and the model handle that. They live in the logic layer: the loop boundary, the null case, the ordering, the invariant that has to hold across a mutation. Prose plans and code both let those stay implicit, and the model then fills them in plausibly-but-wrongly.

A pseudocode plan is worth more than a prose plan *only because it forces those things to be named*. "Handle the edge cases" in prose hides the bug. `if window empty → return 0` either is correct or is visibly wrong in two seconds. That two-second reviewability — by you, before you commit to an implementation — is the entire point. If your plan is no more concrete than prose at the logic layer, it is buying you nothing.

## First: decide whether to pseudocode at all

A pseudocode step on trivial work is pure latency and a cargo-culted ritual. **It is worse than no step.** So gate it.

Ask one question: **could correct-looking code here be subtly wrong in a way that's expensive to discover?**

**Yes → plan first.** Signals:
- Invariants that must hold across mutations (sorted order, balance, no-duplicates, sum-preserved).
- Loops or recursion with non-obvious boundaries, accumulation, or termination.
- A state machine: multiple states and transitions, some illegal.
- Numerical / financial formulas where being slightly off is silently wrong.
- Parsing, evaluation, interpreters, anything that consumes a grammar.
- Concurrency, ordering, races, idempotency.
- Algorithms where the textbook version has a famous off-by-one.

**No → skip it, say so in one line, implement directly.** Signals:
- CRUD endpoints, DB wiring, glue between two libraries.
- Config, plumbing, straight-line transformations with an obvious mapping.
- Rendering and markup.
- Anything where *the code is the spec* — there's no logic to get wrong, only typing to do.

When it's genuinely mixed (a real feature with a tricky core plus plumbing), pseudocode **only the tricky core** and implement the plumbing directly. Don't pseudocode the wiring.

State the verdict before proceeding, e.g. "This is a balanced-tree rebalance — invariant-heavy, planning first" or "This is a CRUD handler, no hidden logic — implementing directly."

## The artifact

When you do plan, the plan must contain all four of these. Each one is where a class of bug hides; omitting a section is choosing not to look for that class.

1. **Data & invariants** — the shapes you operate on, and what must *always* be true of them. Invariants are the highest-value line in the whole artifact: they're what code reviews miss and what tests forget.
2. **Control flow** — the steps / algorithm, language-agnostic. Loop boundaries and recursion bases explicit.
3. **Edge cases & failure modes** — named, not "handle edge cases". Empty input, single element, duplicates, overflow, the null, the boundary, the illegal transition. Each gets a line saying what happens.
4. **Interface contract** — inputs, outputs, and error behaviour. What does it return on bad input — throw, sentinel, clamp?

Keep the whole thing reviewable in under ~60 seconds. If it's longer than that, it has collapsed into code; tighten the abstraction level.

## Constraints (this is what makes it pseudocode, not a draft)

- **No target-language syntax and no real API/library calls.** The moment you write `df.groupby(...)` or `Array.prototype.reduce`, you've stopped planning the logic and started committing to an implementation — and the reader can no longer see the logic for the framework. Write `group rows by key`, not the call.
- **Concrete exactly where prose hand-waves.** Name the boundary (`i from 1 to n-1`), the comparison (`if curr < prev`), the invariant (`heap[parent] ≤ heap[child]`). Vagueness here is the failure mode.
- **Abstract everywhere else.** Don't spell out getters, logging, obvious plumbing.

## Then: implement against the plan

Write the code, using the plan as the spec. As you implement, the plan is your checklist — every edge case listed should have a corresponding branch, every invariant a place it's maintained.

**If the plan turns out wrong while coding, fix the plan, don't just patch the code.** A wrong plan that you silently code around is the worst outcome — it anchors a wrong approach and you lose the verification surface. If implementation reveals the plan was wrong about the approach, stop, correct the plan (a sentence is fine), then continue. The plan and code should agree at the end.

## Example: abstraction level

A task: *"merge overlapping intervals."*

**Too vague (prose, hides the bug):**
> Sort the intervals and merge the ones that overlap, returning the merged list.

**Too concrete (this is just code):**
```
intervals.sort((a,b) => a[0]-b[0])
const out = []
for (const [s,e] of intervals) { ... }
```

**Right level:**
```
Data: list of [start, end], start ≤ end. Output: disjoint list, sorted by start.
  Invariant: output intervals never overlap and are in start order.

Flow:
  sort intervals by start ascending
  result ← empty
  for each interval iv in sorted order:
    if result empty OR iv.start > result.last.end:
      append iv                          # no overlap, new run
    else:
      result.last.end ← max(result.last.end, iv.end)   # extend, don't shrink

Edge cases:
  empty input            → return empty
  single interval        → return [it]
  touching [1,2],[2,3]   → DECIDE: merge (treat touching as overlap) — uses > not ≥
  fully nested [1,9],[2,3] → max() keeps outer end, so handled

Contract: pure; input not mutated; returns new list.
```

That `> vs ≥` line is the whole game — it's the off-by-one that prose would have buried under "merge the ones that overlap", and it's reviewable at a glance before a single line of real code is written.
