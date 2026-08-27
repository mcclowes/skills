---
name: separate-responsibilities
description: Find god files and separate mixed responsibilities into cohesive, independently understandable units. Use when reviewing oversized files, tangled modules, smart and dumb component boundaries, logic mixed with rendering, or code that changes for unrelated reasons.
license: MIT
metadata:
  author: mcclowes
  version: "0.1.0"
---

# Separate responsibilities

Split code when one unit owns several jobs that change for different reasons. Do not split merely to reduce a line count.

## The principle

**A good boundary leaves both sides understandable on their own.**

A god file is defined by mixed responsibilities and tangled change paths, not size alone. A cohesive 300-line module can be healthier than five 60-line files that must all be opened together.

## Spot mixed responsibilities

Look for files or components that combine several of these:

- Data fetching, persistence, or transport.
- State orchestration and workflow transitions.
- Domain calculations or validation.
- Rendering and visual styling.
- Input normalization and output formatting.
- Platform, vendor, or feature-specific branches.
- Several unrelated public entry points.
- Types, constants, and helpers owned by different concepts.

Other signals include imports from unrelated layers, several clusters of state that never interact, distant sections that change for different features, and tests that require unrelated setup.

Before splitting, describe each proposed unit in one concrete sentence. Vague descriptions such as “helpers” or “miscellaneous logic” expose a weak boundary.

## Smart and dumb code

Separate presentation when it has a clear contract: data and callbacks in, rendered output out, with no knowledge of fetching, storage, or workflow state. This creates a dumb component that can be understood, tested, and reused independently.

Keep logic and rendering together when each is meaningless without the other. A render file with a large prop surface shaped entirely by a neighboring controller is not dumb; it is half a component with extra navigation.

Good separations often look like:

- A thin orchestrator plus self-contained branch or screen components.
- A pure domain function plus a caller responsible for effects.
- A hook with a small behavioral interface plus a presentational component.
- A shared visual primitive plus feature-specific composition.

Avoid moving code into files without reducing what a reader must understand. Relocation is not decomposition.

## Choose boundaries by change

Group code that shares invariants and usually changes together. Separate code that has a stable interface and changes independently. Keep locally owned types, constants, and tests beside their owner; move them outward only when several units genuinely share them.

Prefer direct imports for internal modules. Use a barrel only when it defines a real public package boundary.

## Refactoring sequence

Identify responsibilities and their dependencies before moving anything. Extract the clearest self-contained unit first, preserve its behavior behind a narrow interface, then reassess the remainder. Stop when another split would create fragments that require cross-reading.

If asked to look or review, report boundaries without editing. If asked to refactor or fix, preserve behavior and run the relevant checks after each coherent extraction.

## Output

Report each mixed-responsibility unit, the responsibilities it contains, the proposed boundary, and why each resulting piece stands alone. Note large files deliberately left intact because they remain cohesive.
