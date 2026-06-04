# Extract the shared `<Avatar/>`. The "inline so Claude sees everything" argument doesn't hold up.

Short version: the extraction camp is right. The senior's instinct is reasonable in the abstract — locality of behaviour is genuinely valuable for both humans and AI assistants — but Avatar is the wrong place to apply it, and the specific failure modes of 12x duplication hurt AI-assisted work *more* than they help it.

## Why the "self-contained for Claude" argument is weaker than it sounds

The senior is reaching for a real principle: code that's read together should live together, and an AI agent that can see a whole behaviour in one file doesn't have to go chasing imports. That's true for genuinely *local* logic — a one-off layout quirk, a component's own state machine, glue that only makes sense in context.

But Avatar fails the test for a few concrete reasons:

1. **It's a leaf, not a dependency you have to chase.** Following `import { Avatar } from '@/components/Avatar'` is one jump to a self-contained, ~50-line file. Both Claude and a human resolve that trivially — modern tooling (and the agent itself) jumps to definitions constantly. The "chasing an import" cost is near zero for a well-named pure component. The senior is pricing in a cost that barely exists.

2. **Duplication is the thing that actually wrecks AI edits.** This is the crux. When you ask an assistant to "add a `busy` presence state" or "fix the fallback initials for single-word names," with the shared component it makes one edit in one file. With 12 inline copies, it has to (a) *find* all 12 — and it will miss some, because they've already drifted (copy-pasted code never stays identical), (b) apply the change 12 times, and (c) keep them consistent. Every one of those steps is a place for an agent to do a partial, inconsistent job. You're trading a cheap one-hop read for an expensive, error-prone 12-site write. Writes are where AI assistants are most dangerous; reads are cheap.

3. **Context window is a budget, and duplication taxes it.** If a task touches several of these components, the agent pulls 50 redundant lines into context per file. That's ~600 lines of near-identical noise crowding out the stuff that actually differs between those components. Deduplication makes each file's *real* purpose more legible, which is exactly what helps an agent reason well.

4. **One canonical definition kills a class of bugs.** "Why does the avatar render differently on the settings page?" is a question that only exists because there are 12 copies. With one component, the answer is structurally impossible. That's worth more than any locality nicety.

## What "self-contained" should actually mean here

The senior's underlying worry — agents and humans losing the thread by hopping across files — is legitimate, so address it directly rather than by inlining:

- **Make the component obviously discoverable.** `components/Avatar/Avatar.tsx`, exported by name, well-typed props (`size`, `src`, `name`, `presence`). A clear name and a tight prop interface mean an agent grasps the full contract from the import line without even opening the file.
- **Keep the boundary clean and pure.** Avatar is a pure presentational component — props in, markup out, no data fetching, no app-specific coupling. That's the textbook case for extraction: it's reusable, stateless, and identical everywhere. Pure leaf components are the *safest* possible thing to share, because there's no hidden context to lose when you pull them out.
- **Co-locate its own concerns.** Styles/variants, the fallback-initials helper, and a test live next to `Avatar.tsx`. That gives you real locality — everything about Avatar in one folder — without scattering it across 12 consumers.
- **Add a short test.** With one definition, a handful of tests (fallback rendering, presence dot, each size variant) lock the behaviour for every consumer at once. You can't meaningfully test 12 inline copies.

## When the senior would be right

Inlining wins when the markup is *coincidentally* similar rather than *conceptually* the same — i.e. if these 12 blocks looked alike today but you expect them to diverge per-context, premature extraction would force awkward props and conditionals (the classic wrong-abstraction trap). But that's not what you've described. You've described identical Avatar markup with a fixed, well-bounded variation surface (fallback, presence, size) — variation that's already cleanly expressible as props. That's a stable abstraction, not a speculative one.

## Recommendation

Extract `<Avatar/>` into a shared component with a typed prop interface (`size`, `src`, `name`, `presence`), co-locate its styles/helpers/test in one folder, and replace all 12 inline copies. Expect to find small drifts between the copies as you consolidate — reconcile them deliberately, since picking the canonical behaviour is the main judgement call in this refactor.

Don't generalise the senior's rule into "always inline for the AI," though — they're onto something real. Keep genuinely local, one-off logic inline. Avatar just isn't that: it's a reusable, pure, duplicated leaf, which is the single clearest case for extraction whether your readers are human or machine.
