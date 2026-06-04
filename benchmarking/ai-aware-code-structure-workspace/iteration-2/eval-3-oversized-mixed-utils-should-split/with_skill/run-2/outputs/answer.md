# Split it — but along the seams that already exist, not into tiny shards

The "big files are fine for AI now" take is half right, and your file is exactly the case where the other half bites.

Here's the nuance. Large files *are* better than people used to think, because an agent reading one self-contained file beats an agent hopping across four files it'll never bother to open. The reluctance of AI tools to look at adjacent files is real, so co-location and slightly-bigger files genuinely help. But that argument only applies to code that's *cohesive* — code that belongs together because the parts need each other for context.

Your `helpers.ts` is the opposite. By your own description:

- Date formatting
- Currency formatting
- A fetch wrapper
- Form-validation predicates
- Array/object utilities

> "They don't really call each other — it's just where everything landed."

That's the tell. This isn't one coherent concern that grew large. It's five unrelated concerns sharing a filename by accident. The "keep it big" reasoning buys you nothing here, because there's no coupling to preserve — splitting these apart forces *zero* cross-file lookups, since none of them reference each other. You get all the upside of separation with none of the cost.

And at ~550 lines you're well past the point where signal-to-noise starts hurting an agent. When something asks an AI to "add a phone-number validator," you want it to open a 90-line `validation.ts`, not wade through currency math and fetch retry logic to find the right spot. A focused file is a better prompt.

## What I'd do

Split by concern, one file per cohesive group:

```
utils/
  date.ts          // date formatting
  currency.ts      // currency formatting
  http.ts          // the fetch wrapper
  validation.ts    // form-validation predicates
  collections.ts   // array/object utilities
```

Each of these passes the test that matters: **can it be understood in isolation?** Yes — every group is self-contained, mostly pure functions, props/args in and values out. An agent can open `validation.ts` and do useful work without needing anything from the other files. That's the ideal shape.

A few practical notes:

- **Don't over-split.** Resist the urge to go to one-function-per-file. A `validation.ts` with a dozen related predicates is the right grain — it's cohesive and stands alone. Five files is about right for what you've described; fifty would be reflex-splitting and would just scatter context.
- **Keep a barrel only if it's cheap.** Since it's imported all over the app, a `utils/index.ts` that re-exports everything lets you do the split without touching every call site. That's fine. Just be aware barrels can hurt tree-shaking and occasionally create import cycles, so prefer that consumers migrate to the specific module paths over time.
- **Watch for hidden coupling as you split.** You said they don't call each other — verify that. If, say, a validation predicate quietly uses the date formatter, keep that relationship visible (import it explicitly) rather than duplicating. If two groups turn out to be genuinely intertwined, leave those two together.
- **The fetch wrapper is the one to eyeball.** It's the only item here with side effects and likely some real complexity (errors, retries, headers). It deserves its own file regardless, and it's the most likely to want a proper abstraction rather than a loose bag of helpers.

## The general rule to take away

Bigger files win when the contents are *one thing* and the parts need each other — co-location beats scattering. They lose when the file is a junk drawer of unrelated things, because then size is pure noise with no cohesion to justify it. Yours is squarely a junk drawer. Split it by concern, keep each resulting file cohesive and self-contained, and stop there.
