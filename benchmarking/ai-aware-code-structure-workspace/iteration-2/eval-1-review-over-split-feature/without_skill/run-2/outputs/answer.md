# Review: UserBadge folder structure

Short version: this is over-split for what it is, and I'd consolidate. The fact that you use AI assistants heavily is actually an argument *against* this layout, not for it.

## What you have

```
UserBadge/
  index.ts              # re-export
  UserBadge.view.tsx    # JSX only
  UserBadge.logic.ts    # 40 lines
  UserBadge.styles.ts
  types.ts
```

Five files for a single badge component. Each is "small and single-purpose," which sounds like a virtue but here it's the symptom. You've taken one cohesive unit and shattered it along technical seams (markup / logic / styles / types) rather than along meaningful boundaries.

## Why "small and single-purpose" misleads you here

"Single-purpose" is being applied at the wrong granularity. The *component* is the single purpose. JSX, its 40 lines of logic, its styles, and its prop types aren't separate purposes — they're the constituent parts of one thing. Splitting them doesn't reduce coupling; it just spreads tightly-coupled code across file boundaries. Change the badge and you're almost always touching the view *and* the logic *and* the types together. That's the tell: when files always change in lockstep, they want to be one file.

The classic separation that earns its keep is **reusable logic vs. UI** — a hook or pure function that more than one component uses, or that you want to unit test in isolation. A 40-line `.logic.ts` used by exactly one view is not that. It's just the component's body that's been moved next door.

## The AI angle specifically

Heavy AI-assisted development changes the cost calculus, and it pushes toward *fewer, fuller* files:

- **Context assembly cost.** To understand or edit `UserBadge`, an assistant has to open and reconcile five files. Each hop is a chance to miss context, edit the wrong layer, or hallucinate a prop that doesn't line up across `types.ts` and `.logic.ts`. One file that holds the whole component is read in a single pass with no cross-file reasoning.
- **Edit blast radius.** A trivial change ("add a `tooltip` prop") becomes a multi-file edit: types, logic, view. More files touched = more diff surface = more places for an agent to get it subtly wrong, and more for you to review.
- **Co-location beats indirection.** LLMs do best when the relevant code is physically adjacent. `index.ts` re-export barrels and split layers add indirection that an agent has to chase, burning tokens and attention on plumbing rather than the actual problem.
- **The split doesn't even buy isolation.** The styles, types, and logic here are meaningful only in the context of the view. Reading any one of them alone tells the agent (or a human) very little.

## What I'd do

Collapse it to one or two files:

```
UserBadge/
  UserBadge.tsx     # types + logic + JSX together
  index.ts          # only if your import conventions require the barrel
```

Or, if you don't need the folder at all, just `UserBadge.tsx`. Keep `types.ts` separate **only** if the types are shared by other modules. Keep styles separate only if your styling system forces it (e.g. a `.module.scss` companion) — and a CSS/SCSS module is a fine exception because it's a different language and tooling, not arbitrary fragmentation.

Pull `.logic.ts` back out into its own file *later, if and when* a second consumer appears or the logic grows enough to warrant isolated tests. Split on demonstrated need, not on a speculative template.

## The real risk

The danger isn't this one badge — it's that this is a *house pattern*. Five files per trivial component, multiplied across a codebase, produces an explosion of tiny files where every feature is a scavenger hunt. That tax is paid on every single read and edit, by humans and assistants alike. A consistent "one component, one file until proven otherwise" rule scales far better.

## Rule of thumb

- Split when files **change independently**, when logic is **genuinely reused**, or when a file gets large enough that finding things in it is the bottleneck (think hundreds of lines, not forty).
- Don't split a single cohesive unit along technical layers (view/logic/styles/types) just because you *can*.
- For AI-assisted work, bias toward **co-location**: keep the things that change together in the same file so the whole unit fits in one read.

Net: consolidate `UserBadge` down to one file (plus a barrel and a stylesheet only if your conventions demand them), and reserve the logic/types split for the cases that have actually earned it.
