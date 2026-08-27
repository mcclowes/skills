---
name: make-implicit-explicit
description: Find magic numbers, strings, booleans, hidden domain rules, and anonymous configuration, then give important concepts clear names and scope. Use when reviewing unexplained literals, duplicated constants, implicit conventions, or code whose intent is encoded only in values.
license: MIT
metadata:
  author: mcclowes
  version: "0.1.0"
---

# Make implicit concepts explicit

Name values and rules when the name carries information the literal cannot.

## The principle

**Extract the meaning, not every literal.**

`0`, `1`, an empty string, and a one-off spacing value are often obvious in context. Turning all of them into constants adds indirection without adding knowledge. A value is magic when a reader cannot tell why it is correct, when it must stay synchronized elsewhere, or what would justify changing it.

## What to look for

- Numeric thresholds, timeouts, limits, offsets, status codes, and retry counts.
- Strings used as protocol values, storage keys, event names, routes, or discriminators.
- Boolean arguments whose meaning is invisible at the call site.
- Repeated literals that must remain consistent.
- Formulas whose coefficients or units are unstated.
- Array positions, bit masks, sentinel values, and ordering assumptions.
- Domain rules buried inside conditionals rather than named predicates.
- Configuration mixed into operational code.

Ask three questions: what does this value mean, why is it this value, and where should that decision live?

## Choose the right expression

- Use a **local named constant** when one function owns the decision.
- Use a **module constant** when several operations in one concept share it.
- Use a **domain type or enum** when callers choose among a closed set of meaningful states.
- Use an **options object** instead of positional booleans or several same-typed arguments.
- Use a **named predicate or function** when the rule is more important than its ingredients.
- Use **configuration** only when the value legitimately varies by environment or deployment.
- Use a **design token** when repeated styling shares a semantic role, not just a numeric value.

Keep definitions near the code that owns them. Do not create a dumping-ground constants file. Promote a definition outward only when multiple independent consumers share the same concept.

Include units in names or types where confusion is plausible: `timeoutMs`, `retentionDays`, or a duration type beats `timeout`.

## Avoid cosmetic naming

`const THREE = 3` and `const VALUE = "active"` preserve the mystery. A useful name explains the role: `MAX_LOGIN_ATTEMPTS` or `ACCOUNT_STATUS_ACTIVE`. When the reason is non-obvious and cannot fit in the name, add one short comment explaining why, not what.

If asked to look or review, report findings without editing. If asked to refactor or fix, preserve behavior, keep scope narrow, and run the relevant checks.

## Output

Report the literal or rule, its current locations, the concept it represents, and the narrowest useful replacement. Distinguish high-value hidden rules from harmless literals that should remain inline.
