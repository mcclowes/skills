# Central types file: good or not?

Short version: a single `types.ts` is fine while it's small, but at 400 lines imported by basically everything, you've outgrown it. The problem isn't "single source of truth" as a principle, it's that one giant shared file works against the way you're now editing code (through Claude Code), and against clean dependency boundaries. I'd split it, but not in the way the old "one file per type" instinct would push you.

## Why it bites, especially with an agent

A couple of things are true at once here:

- **The file is a low-signal prompt.** When Claude opens `types.ts` to work on one feature, it's loading 400 lines of unrelated type definitions into context. Most of it is noise for any given task. High signal-to-noise gives better output; a kitchen-sink types file is the opposite.
- **It hides the real dependency graph.** "Every component and service imports from it" sounds like a strength, but it means a change to one type sits in a file that everything depends on. There's no signal about what actually uses what. An agent editing a checkout type can't tell from the file whether it's touching something three other services rely on.
- **It pulls context away from where work happens.** The agent is reluctant to go look at adjacent files. If the `Order` type lives in `types.ts` but you're editing `order-service.ts`, that's a cross-file lookup the agent often won't make — so it works from a partial picture and gets the shape subtly wrong.

So the central file optimises for one thing (a single place to define types) at the cost of the things that matter more day to day: focused context and visible coupling.

## What to do instead: co-locate types with what owns them

The useful principle is **a type should live next to the code that owns it**, and be understood in isolation there.

- A type used by exactly one module belongs **in that module's file**, not in `types.ts`. If `OrderService` is the only thing that defines and produces `Order`, define `Order` in `order-service.ts` and export it. Now when the agent opens that file, the type and its usage are in front of it together — no lookup, no guessing at shape.
- A type shared by a handful of modules in one feature belongs in a **feature-local types file** (`features/checkout/types.ts`), not the global one.
- The genuinely cross-cutting, app-wide primitives — `UserId`, `ApiResponse<T>`, a few core domain entities — those can stay in a shared types file. That's a legitimately small, stable set. The mistake is letting everything else accumulate there too.

This is just co-location: types that are always changed alongside their owning code should sit with it, so the agent works from a complete picture instead of chasing definitions across files.

## How aggressively to split

Don't shatter it into one-type-per-file — that swings too far the other way and creates a pile of tiny files that only make sense when read together, which is exactly the cross-file lookup pattern that trips agents up. Instead:

1. Move each type to the module that owns it where there's a clear single owner.
2. Group the rest by feature into feature-local type files.
3. Keep a deliberately small global file for true app-wide primitives only.

A 150-line feature types file that's cohesive is completely fine — line count isn't the trigger. Coupling and signal-to-noise are. The test for each move: can someone (or Claude) understand this type, and edit code that uses it, without also opening the global file? If yes, you've put it in the right place.

## One caveat

If a meaningful share of those 400 lines genuinely is shared-everywhere primitives, don't force a split that produces circular imports or scatters a tightly-related cluster. Co-location only helps when each resulting file stands on its own. Where two types only make sense together, keep them together.

## Bottom line

Single source of truth is the right instinct; "single *file*" is the part to drop. Push types down to the code that owns them, group the rest by feature, and keep only the truly global primitives central. You'll get more focused prompts for the agent, a dependency graph you can actually see, and fewer subtle "the shape was defined two files over" breakages.
