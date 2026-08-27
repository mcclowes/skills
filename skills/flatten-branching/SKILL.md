---
name: flatten-branching
description: Simplify repeated, nested, or scattered control-flow decisions by resolving each branch once at the highest useful point. Use for repeated status or mode checks, nested conditionals or ternaries, and flags threaded below the point that owns the decision. Do not use for general file splitting, duplication, naming, or validation reviews.
license: MIT
metadata:
  author: mcclowes
  version: "0.1.0"
---

# Flatten branching

Resolve a decision once, as high as the information allows, then keep each branch straight-line below it.

## Find costly forks

Look for:

- The same status, mode, variant, capability, or feature flag consulted repeatedly in one flow.
- Nested conditionals or ternaries whose combinations must be held in mind together.
- A decision made independently in several children when their common owner already knows it.
- A flag passed through layers that do not otherwise care about it.
- Branches that duplicate meaningful work before converging again.

Count repeated consultations and nesting depth before changing the code. These are diagnostic signals, not targets to game.

## Choose the boundary

Resolve the fork at the highest point that knows the deciding information and owns the divergent behavior. Keep a decision local when hoisting it would duplicate work, inflate an interface, or force unrelated callers to know about it.

Use the smallest shape that makes each path readable:

- An early return or guard clause for exceptional paths.
- A named predicate for a domain rule hidden in a compound condition.
- A switch or dispatch table for several stable cases.
- A thin orchestrator plus self-contained branches when the cases have distinct behavior or state.
- One shared operation after branches reconverge, rather than a copy in every branch.

Do not split a component or module merely to make every leaf conditional-free. If the proposed pieces cannot be understood independently, keep them together and simplify the local control flow instead.

## Preserve behavior

Keep outputs, effects, calls, error behavior, and public interfaces unchanged unless the user requests a behavior change. Characterize meaningful branch differences before refactoring, and verify each still exists afterward.

If asked to look or review, report findings without editing. If asked to refactor or fix, make the smallest behavior-preserving change and run the relevant checks.

## Output

Report the decision, its locations, consultation count and nesting depth before and after, the chosen boundary, and any tempting fork deliberately left local.
