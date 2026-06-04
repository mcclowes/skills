# Extract the shared `<Avatar/>` — the extract camp is right

Extract it. The "keep it inline so Claude sees everything self-contained" argument sounds AI-friendly but it actually works against you, both for the AI and for the humans. Here's the reasoning.

## Why the inline argument doesn't hold up

The senior's premise is that an import is a cost — Claude has to "chase" it. In practice that cost is tiny and getting tinier:

- **Resolving one import is cheap for an agent.** Opening `Avatar.tsx` is a single, cheap, deterministic step. Modern coding agents do this constantly and reliably. You're trading one extra file-open against twelve copies of 50 lines of logic that the model now has to read, diff, and reason about every time it touches any of those components.
- **Self-contained ≠ comprehensible.** A 50-line inline avatar block buried in the middle of a 12th component isn't "self-contained context," it's noise. When Claude opens `UserCard.tsx` to fix something about the card, the avatar markup is 50 lines of distraction competing for attention with the thing you actually asked about. A single `<Avatar size="lg" presence={user.status} />` line communicates intent far better than the full fallback-initials-and-presence-dot implementation.

## Why duplication is *worse* for AI assistants specifically

This is the part the inline camp has backwards. The failure mode of LLM-assisted editing is not "couldn't find the import." It's **inconsistent edits across duplicated code**:

- You ask Claude to "make the presence dot green when online." With one `<Avatar/>`, that's one edit in one place, correct everywhere. With 12 inline copies, the agent edits the 3-4 files in its current context, declares success, and silently leaves 8 copies stale. Now your avatars disagree across the app and nobody notices until QA.
- Each inline copy will also have **drifted** over time — copy-paste never stays identical. The agent then has 12 *slightly different* versions to reconcile, which is strictly harder than reasoning about one canonical component. Drift is the real enemy of AI legibility, and inlining guarantees it.
- Twelve copies of the same logic inflate the surface area the model has to search, read, and keep consistent. That's more tokens, more chances to touch the wrong copy, more chances to introduce a subtle divergence.

A single well-named component is the *most* AI-legible structure available: the name documents intent, the props document the variation points (size, presence, fallback), and there's exactly one place to change behaviour.

## The one legitimate concern, and how to neutralise it

The inline camp's real, valid worry is **hidden complexity** — that `<Avatar/>` becomes an over-abstracted prop soup nobody can read, the kind of "spooky action at a distance" that genuinely does hurt comprehension. The answer isn't to avoid extraction, it's to extract *well*:

- Keep it a **pure, presentational component**: props in, markup out, no data fetching, no context reaching, no surprise side effects. This is the easiest possible thing to extract because there's no shared state to untangle — it's the textbook case for a shared component.
- **Keep the prop surface honest.** `size`, `src`, `name` (for initials), `presence`. If you find yourself adding a tenth boolean flag, that's the signal to split variants, not a reason to regret extracting.
- **Co-locate everything**: `Avatar.tsx`, its styles, and its tests in one folder. One obvious home that any agent or human resolves instantly.
- Put a one-line doc comment at the top stating what it is and its variants. That's the "self-contained context" the senior wants — delivered once, canonically, instead of smeared across 12 files.

## Bottom line

Extract `<Avatar/>` as a pure presentational component. The "AI sees everything inline" intuition optimises for a near-zero cost (one import resolution) while paying a large, recurring one (12 copies that drift and get edited inconsistently). DRY isn't just an aesthetic preference here — for an LLM-heavy workflow, a single source of truth is the single biggest thing you can do to keep edits correct and consistent. The duplication is the AI hazard, not the import.
