---
name: consolidate
description: Find and remove meaningful code duplication without overabstracting. Use when reviewing reuse opportunities, repeated styles or components, copied logic, duplicated constants or assets, or several implementations of the same concept.
license: MIT
metadata:
  author: mcclowes
  version: "0.1.0"
---

# Consolidate repeated concepts

Remove duplication when it represents one concept that should change in one place. Similar-looking code is evidence to investigate, not an automatic instruction to abstract.

## The principle

**Abstract shared meaning, not shared syntax.**

An extraction earns its keep when the copies express the same rule, presentation, behavior, or domain concept and should evolve together. Leave them separate when their resemblance is incidental, their reasons differ, or independent change is likely.

Two examples are enough to investigate, not enough to force an abstraction. Prefer a small local extraction over a speculative general framework.

## How to inspect

Search beyond exact text matches. Look for:

- Blocks with the same shape but renamed variables or reordered statements.
- The same domain rule implemented in handlers, validators, selectors, or services.
- Repeated markup and styles that render the same visual concept.
- Components that differ only by content, one widget, or a small behavior.
- Constants, assets, queries, mappings, or formatting rules copied across files.
- Fixes that would need to land in several places to remain consistent.

For each candidate, name the concept the copies share. If it cannot be named without vague words such as `common`, `shared`, or `helper`, the abstraction probably is not ready.

## Choose the smallest useful form

- **Repeated value with one meaning:** extract a narrowly scoped named constant or token.
- **Repeated calculation or rule:** extract a pure function named for the domain result.
- **Repeated styling only:** extract a style token or primitive before extracting markup.
- **Repeated markup and styling:** extract a dumb component with a narrow props contract.
- **Stable behavior plus presentation:** extract a component or hook only when callers share the behavior, not merely the appearance.
- **Mostly shared structure with one deliberate variation:** use a prop or slot when it makes the call site clearer than two copies.
- **Different state models or change pressures:** keep separate, even if today they look alike.

Do not build a configuration system for hypothetical variants. Do not hide a five-line expression behind an abstraction that takes longer to understand than the copies.

## Styles and components

Use this ladder, stopping at the first level that captures the real repetition:

1. Shared value or design token.
2. Shared style object, class, or mixin.
3. Dumb presentational component: props in, rendered output out.
4. Smart component or hook with a stable behavioral contract.

Repeated pixels do not necessarily share meaning. Promote a value into a global token only when its semantic role is shared, such as `surface-muted`, not merely because three unrelated elements happen to use the same gray.

## Preserve behavior

First characterize the copies' meaningful differences. After consolidation, verify those differences still exist and that callers keep the same output, effects, error behavior, and network interactions.

If asked to look or review, report candidates without editing. If asked to refactor or fix, make the smallest behavior-preserving consolidations and run the relevant checks.

## Output

For each candidate, report the locations, shared concept, recommendation, and confidence. Include deliberate non-extractions where the similarity is tempting but the abstraction would couple unrelated code.
