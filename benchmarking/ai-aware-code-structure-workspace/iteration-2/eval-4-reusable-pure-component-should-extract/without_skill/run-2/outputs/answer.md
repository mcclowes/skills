## Extract the `<Avatar/>` component. The "keep it inline for the AI" argument doesn't survive contact with the actual failure modes.

The instinct behind the inline camp isn't crazy — self-contained files genuinely do help an AI assistant, because the model only sees what's in its context window, and chasing imports costs tokens and turns. But that principle is being misapplied here. "Locality of behaviour beats DRY" is a real and useful heuristic, and it's the right call for *trivial, incidental* duplication. A 50-line block with fallback logic, presence state, and size variants, copied 12 times, is neither trivial nor incidental. It's a real component wearing a disguise.

Here's why the AI argument actually cuts the *other* way:

### 1. Duplication is where AI assistants do the most damage

The failure mode you should worry about with AI isn't "Claude had to open one extra file." It's **inconsistent edits across copies**. When you ask an assistant to "fix the avatar fallback so initials use the right contrast" or "add a `xs` size," one of two bad things happens:

- It edits the 2-3 copies that happen to be in its context and silently misses the other 9-10. Now you have drift that no one notices until a designer files a bug.
- It *does* try to find all 12, burning a big chunk of its context budget grepping and re-reading near-identical blocks, and still has no compiler-enforced guarantee it got them all.

A single `<Avatar/>` turns "change this in 12 places, hope you found them all" into "change one file, every call site updates." That's strictly better for an AI agent, because the agent's weakness is *consistency at scale*, not *opening files*. You're optimising against the wrong risk.

### 2. The "chasing an import" cost is tiny and getting tinier

Following one import to a well-named `Avatar.tsx` is one extra read. Modern assistants (and the humans pairing with them) handle that fine — it's the bread-and-butter of navigating any real codebase. Compare that to the cost of the duplication: 12 × 50 = ~600 lines of repeated markup that bloat *every* file the avatar appears in, making each of those 12 components harder to read and reason about for both Claude and humans. You're paying the locality "tax" everywhere to save an import you pay once.

### 3. Self-contained is good; self-contained *via copy-paste* is not

The senior is conflating two different things. "Self-contained" is valuable when a file owns its own distinct logic. But these 12 components don't each own avatar logic — they all want *the same* avatar. Inlining doesn't make them self-contained in a meaningful sense; it makes them carry a duplicated dependency they can't see is shared. The honest, legible version of "this component uses an avatar" is `import { Avatar } from '...'`, not 50 lines that happen to be identical to 11 other files.

### What I'd actually do

- Extract `<Avatar/>` with a tight, obvious prop API: `src`, `name` (for initials fallback), `size`, `presence`. Keep it a **pure presentational component** — no data fetching, no context coupling — so it stays trivial to drop in anywhere.
- Co-locate its variants and fallback logic in the one file, ideally with a short doc comment at the top stating what it does. That gives the AI the "everything in one place" benefit the senior wants, just at the *component* boundary instead of smeared across 12 call sites.
- Name it discoverably and put it where shared UI lives (`components/ui/Avatar.tsx` or wherever your design-system primitives sit) so an assistant finds it by convention without searching.
- If you want to genuinely help future AI edits, add a couple of tests for the fallback-initials and presence-dot behaviour. That's the real safety net — it means an assistant can refactor the one component with confidence instead of guessing across copies.

### The one caveat worth naming

There's a version of this where extraction goes wrong: if you over-abstract it into a configuration monster with 15 props, conditional slots, and three layers of wrapper components to handle every future case, you've made it *harder* to understand, not easier — for humans and AI alike. The win comes from a small, boring, pure component. Resist the urge to make `Avatar` solve problems you don't have yet. If a 13th use case needs something genuinely different, let it diverge rather than bending the shared component around it.

**Bottom line:** extract it. The shared-component camp is right, and they're right *because* you lean on AI assistants, not in spite of it. The thing AI is worst at — keeping a dozen copies in sync — is exactly the thing a single `<Avatar/>` eliminates. The thing the senior is protecting against — one extra import hop — is the thing AI handles trivially.
