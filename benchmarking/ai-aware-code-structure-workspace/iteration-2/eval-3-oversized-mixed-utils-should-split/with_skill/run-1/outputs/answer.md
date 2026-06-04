# Split it — but for the right reason, not the line count

The "big files are fine for AI now" thing is half-true, and your case is exactly where it falls apart.

It's true that the old "if it doesn't fit on one screen, split it" rule was calibrated for human scrolling, and agents handle larger files fine — roughly up to a few hundred lines before quality starts to degrade. So 550 lines isn't automatically a problem, and you shouldn't split just because a linter or an old instinct says so.

But the thing that actually matters for an AI agent isn't size, it's **signal-to-noise**. When an agent opens a file, everything in it costs tokens and attention. A focused file is a better prompt than a sprawling one. Your `helpers.ts` is the worst version of this: it's both large *and* incoherent. Five unrelated concerns living together means that any time an agent edits one currency function, it's also carrying date logic, a fetch wrapper, validation predicates, and array utilities as pure noise. None of that helps it; all of it dilutes context.

The deciding factor here is your own observation: **these functions don't call each other.** That's the tell. The real test for whether to split isn't "is this a separate concern?" — it's "can each piece be understood in isolation?" For tightly-coupled code, splitting is harmful because it just doubles the cross-file lookups an agent is reluctant to perform. But your functions are already independent. There's zero coupling cost to separating them, and a real signal-to-noise win. This is the easy case: split.

## How I'd split it

Group by the natural seams that already exist. Roughly:

```
utils/
  dates.ts        // date formatting
  currency.ts     // currency formatter
  http.ts         // fetch wrapper
  validation.ts   // form-validation predicates
  collections.ts  // array/object utilities
```

Each file is self-contained — props in, output out, no dependence on a sibling to make sense — which is exactly what makes a split safe for an agent. An agent landing in `validation.ts` to add a predicate sees only validation code and isn't paying attention tax on date formatting it'll never touch.

A few practical notes:

- **Don't make a barrel `index.ts` that re-exports everything** just to preserve `import { x } from './helpers'`. A barrel re-introduces the exact problem you're solving: it becomes a fan-out point an agent has to chase through, and it encourages importing the whole grab-bag again. Update imports to point at the specific module. It's noisier in the diff once, cleaner forever.
- **Co-locate tests with each module** (`dates.test.ts` next to `dates.ts`). Same isolation logic — an agent editing the dates file has its tests right there.
- The thin fetch wrapper is the one to watch. If it's genuinely a couple of lines with no shared state, `http.ts` is right. If it grows config, interceptors, or error handling that other code depends on, that's where you'd reach for a real abstraction rather than just a file.

## The general rule to take away

Size alone wasn't your problem and it's a bad trigger for splitting. The problem is **mixed, uncoupled concerns** — which hurt an agent precisely because they lower signal-to-noise without buying any cohesion. When code is coupled and only makes sense together, lean toward keeping it in one file even past a few hundred lines, and reach for a named abstraction (a hook, a function, a module with a clear interface) before reaching for a new file. Here you have neither coupling nor a case for a single abstraction — you have five independent toolkits sharing a filename by accident. Split them.
