# Split it. This is the case big-file advice doesn't apply to.

Short version: yes, split it — but not because of line count. Split it because of what's *in* it. The "big files are fine for AI now" advice is real, but it's being misapplied here. Let me unpack why.

## What the "big files are fine" claim actually means

The grain of truth: a 550-line file is not big, and chopping a file into ten 50-line fragments purely to hit some line-count target is counterproductive. It scatters related logic, forces readers (human and AI) to jump between tabs to follow one thought, and inflates the import graph for no benefit. Arbitrary size limits are a bad heuristic. On that, the advice is right.

But "size doesn't matter much" is not the same as "cohesion doesn't matter." The thing that makes a file good or bad to work with — for a person *or* an agent — is whether everything in it belongs together. Your file fails on exactly that axis, and it would fail even if it were 200 lines.

## Why your `helpers.ts` is the bad kind of big

You described it yourself, and it's a textbook junk drawer:

- Date formatting
- Currency formatting
- A fetch wrapper
- Form-validation predicates
- Array/object utilities

Your own words: "They don't really call each other — it's just where everything landed." That's the tell. This isn't one module that happens to be long; it's five unrelated modules sharing a filename by accident. The file has **zero internal cohesion**. The only thing binding these functions together is that someone needed somewhere to put them.

That's the difference that matters:

- **Cohesive and long** (e.g. a 600-line date library where everything is about dates) → fine, leave it.
- **Incoherent and any length** (your case) → split it, regardless of line count.

## The "imported all over the app" detail makes splitting *more* important, not less

This is the part I'd push back on hardest if you were leaning toward leaving it. A grab-bag utility module that's imported everywhere is the worst possible thing to be a grab-bag, for a few concrete reasons:

1. **Import-graph noise.** Every file that needs `formatCurrency` currently pulls in a symbol-level dependency on a module that also contains your fetch wrapper and validators. Tooling, bundlers (depending on tree-shaking quality), and reviewers all see a fatter dependency than reality. A component that only formats dates looks like it depends on your network layer.

2. **Change blast radius.** When you (or an agent) edit the fetch wrapper, every importer of `helpers.ts` is nominally "touched" in the dependency sense. Diffs, blame, and "what could this change have affected" reasoning all get muddier.

3. **It's a magnet.** Junk drawers grow. A file literally named `helpers` with five unrelated concerns *invites* the sixth, seventh, and eighth thing to land there too. Today it's 550 lines; the structure guarantees it becomes 900. Splitting now sets a boundary that stops the accretion.

## Why this specifically matters for AI agents (since that's your framing)

The case for splitting is *stronger* in an AI-assisted codebase, not weaker:

- **Retrieval and context.** When an agent is asked to "fix the currency rounding bug," a well-named `currency.ts` is a precise target. With `helpers.ts`, the agent either pulls the whole 550-line file into context (burning tokens, diluting attention with irrelevant date/fetch/validation code) or relies on fuzzy search and risks editing the wrong thing.

- **Naming is the index.** Agents navigate largely by file and symbol names. `formatDate` living in `date.ts` is self-documenting; living in `helpers.ts` it's invisible until something reads the whole file. Good filenames are free documentation that both humans and models lean on.

- **Smaller, safer edits.** A change scoped to `validation.ts` can't accidentally clobber the fetch wrapper. The blast radius of an agent's edit is bounded by the file, so cohesive files mean safer autonomous edits.

The "big files are fine for agents" idea usually comes from the observation that modern models have large context windows and can hold a long file in their head. True — but context window is not the binding constraint here. *Precision* is. You want the agent to find the right code fast and change only the right code. Incoherent files defeat both.

## What I'd actually do

Split by concern, not by line count. Roughly:

```
utils/
  date.ts          // date formatting
  currency.ts      // currency formatting
  validation.ts    // form-validation predicates
  array.ts         // (or collection.ts) array/object utilities
  http.ts          // the fetch wrapper
```

A few practical notes:

- **One concern per file, sensible names.** Each file should be describable in a single phrase without "and." If you can't name it without "and," it's still a junk drawer.
- **The fetch wrapper probably wants to graduate.** A thin fetch wrapper that's imported app-wide is often the seed of your networking/data layer. Give it room (`http.ts` or `lib/api`) rather than treating it as a "util" — it'll grow real concerns (auth headers, error handling, retries) and you don't want those landing in a generic utils folder.
- **Don't pre-fragment.** If "array/object utilities" is genuinely cohesive, keep it as one file even if it's chunky. Split when concerns diverge, not when a line counter trips.
- **Migration is cheap and mechanical** — exactly the kind of task to hand to an agent. Move functions into the new files, update imports. If you want a soft landing, keep `helpers.ts` temporarily as a barrel that re-exports from the new modules, then remove it once imports are migrated. (I'd lean toward just updating the imports directly so you don't leave the junk-drawer name lingering as a tempting target — but the barrel is a fine intermediate step for a large codebase.)
- **This is a good moment to add tests** if these don't have them. Pure functions like formatters and validators are trivial to test, and the split gives each a clear home (`date.test.ts` next to `date.ts`).

## The one-line takeaway

The line count was never the problem and was never the reason to split. The problem is that five unrelated things share one filename, and that file is imported everywhere. Split by concern. Both your future self and any agent working in this codebase will navigate it faster and break it less often.
