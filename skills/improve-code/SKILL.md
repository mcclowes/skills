---
name: improve-code
description: Review code for structural improvement opportunities across branching, duplication, mixed responsibilities, and hidden concepts. Use for broad requests to clean up, simplify, refactor, or identify code smells; use a narrower specialist skill when the request names one specific concern.
license: MIT
metadata:
  author: mcclowes
  version: "0.1.0"
---

# Improve code deliberately

Review code through a small set of opinionated lenses. Find changes that reduce the amount a reader must hold in their head without replacing straightforward code with abstraction machinery.

## Scope the mode

Honor the verb in the request:

- **Look, review, audit, or find:** inspect and report. Do not edit.
- **Improve, clean up, refactor, or fix:** make the supported changes, preserve behavior, and run relevant checks.

If the user names one concern, stay on that concern. Use the full review only for a broad improvement request.

## Review lenses

### Branching

Find the same condition consulted repeatedly, nested conditionals, and forks resolved too low. Resolve a branch once at the highest useful point, then keep each branch straight-line. Do not trade repeated conditions for duplicated logic.

### Duplication

Find repeated domain rules, behavior, markup, styles, constants, and assets. Abstract only when the copies represent one concept that should evolve together. Prefer the smallest useful form: token, constant, function, dumb component, then smart abstraction.

### Responsibilities

Find files that combine unrelated jobs or change for unrelated reasons. Split only along boundaries that leave each result independently understandable. Separate smart orchestration from dumb presentation when the presentation has a narrow contract; keep them together when the proposed halves need constant cross-reading.

### Hidden concepts

Find magic numbers, strings, booleans, anonymous configuration, and buried domain rules. Name a value when the name explains why it is correct. Leave obvious literals inline, and keep definitions near their owner.

## Rank opportunities

Prioritize changes that:

1. Remove duplicated business rules or inconsistent behavior.
2. Collapse repeated or nested control flow.
3. Give a mixed-responsibility unit a stable boundary.
4. Name a hidden domain decision.
5. Reduce repeated presentation without inventing a premature design system.

Treat broad line-count reductions and abstraction counts as weak evidence. The target is lower cognitive load and safer change.

## Guardrails

- Preserve rendered output, effects, network calls, errors, and public interfaces unless a behavior change is explicitly requested.
- Do not introduce a framework, registry, generic helper layer, or configuration system for hypothetical future cases.
- Do not split a cohesive file just because it is long.
- Do not merge code that looks similar but has different reasons to change.
- Reassess after each coherent change; stop when the next move adds more navigation than clarity.

## Output

For a review, report findings by confidence and impact, with locations, reasoning, and the smallest recommended change. Include tempting candidates deliberately left alone.

For a refactor, summarize each changed area by lens, state the preserved behavior, and report checks honestly.
