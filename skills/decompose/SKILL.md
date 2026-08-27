---
name: decompose
description: Flatten logical forking — resolve each branch once, as high as possible, and make everything below it straight-line
---

# Decompose for clarity

Refactor $ARGUMENTS (default: the files changed on this branch) to **flatten logical forking**. This is a behaviour-preserving structural refactor — the rendered output and the network calls must be identical when you're done, unless a fix is explicitly called out below.

Part of the audience for this code is an AI agent reading it cold. Optimise for a reader who has only the one file open.

## The principle

**Branch once, as high as the information allows, then be straight-line below.**

Repeated and nested forks multiply complexity; a single fork adds to it. If a `status`, a feature flag, or a platform check is consulted in four places in one function, the reader has to hold the whole cross-product in their head — and no single place in the code answers "what does this look like when status is error?".

Resolve the fork exactly once, at the highest point where the value is known. Everything downstream of that point should not know the fork exists.

Count it before and after. For each file, how many times is the same condition consulted, and how deep do conditions nest? Both numbers should drop, and ideally every leaf should reach zero.

```tsx
// before: status consulted 4× in one return, twice as a 3-way ternary
<Label>{status === 'error' ? t('errorTitle') : status === 'success' ? t('successTitle') : t('title')}</Label>
{status === 'idle' && <CloseButton />}
{status === 'error' ? (<>…</>) : status === 'success' ? (<>…</>) : (<>…</>)}

// after: consulted once, in one place, and never again downstream
<WalletPayBottomSheet ref={ref}>
  {status === 'error' && <WalletPayError onClose={onClose} />}
  {status === 'success' && <WalletPaySuccess onClose={onClose} />}
  {status === 'idle' && <WalletPaySplash card={card} onClose={onClose} onAfterProvision={handle} />}
</WalletPayBottomSheet>
// WalletPayError has no conditionals at all and doesn't know a status enum exists
```

## What to look for

1. **A condition consulted more than once in one scope** — the same `status`/`mode`/`variant`/flag read in the title, the buttons, and the body. This is the main target.
2. **Nested ternaries or conditions inside conditions.** Depth is worse than count.
3. **A fork resolved too low.** A capability flag checked inside each of three field components when it could be checked once by their parent — or the reverse, a flag threaded down through props when only one leaf cares.
4. **Fork duplication.** Two branches of a config or platform fork that each inline near-identical markup, so a change has to land twice.
5. **Validation that only happens on the server.** Fields that could be checked as the user types, but instead wait for a submit round-trip and map an error code back onto a field. This is a fork too — it splits "how a field fails" across two distant places.
6. **Vendor or instance names on a general concept.** `ApplePayX` when the thing is really about wallets.
7. **Duplicated assets or constants.** The same SVG, string, or style object copy-pasted per brand/theme/locale when nothing about it actually differs.

## How to fix each

**Repeated condition → shell + one component per branch + thin orchestrator.**

- The shell is dumb: it owns the chrome (modal, card, layout, backdrop, background styling), takes `children`, and knows nothing about branches.
- Each branch gets its own file: one component, no conditionals, a flat return. It imports only what that branch needs.
- A thin `index.tsx` owns the state, the handlers, and the one mapping from state to child. It should read as a table of contents and fit on one screen.
- Shared styles stay in one `styles.ts` next to them.

**Fork resolved too low → hoist it.** Resolve at the highest point where the value is known and the branches diverge. If both branches of a hoisted fork converge again later (same submit call, same success alert), that convergence is one shared function taking a payload, not two copies — flattening the render fork must not leave a duplicated logic fork behind it.

**Fork duplication → one component, defined once, used from both call sites.** Where the fork is only "which input widget", let one component take the switch as a prop. Where the branches have genuinely different state models, give each its own component behind a shared prop shape — but factor out whatever logic they both need rather than implementing it twice.

**Server-only validation → push the rule into the component that owns the field.** "New must differ from old" belongs in the new-password component; "confirm must match new" belongs in the confirm component. Report validity upward via a single `onValidityChange`-style callback so the submit button can disable itself. Keep the server error path — client checks are additive, not a replacement.

**Vendor naming → rename to the concept.** Directory, component, props interface, and imports in one pass. Leave translation keys alone unless renaming them is trivially safe.

**Duplicated assets → a single shared component in `atoms/`,** imported everywhere. Don't build a per-brand override mechanism until a brand actually needs one.

## Rules

- **No nested ternaries in JSX.** A flat list of `cond && <X />` at one level is fine; nesting means you haven't hoisted yet.
- **One component per file**, named for what it renders, in a directory named for the group.
- **A leaf component should have narrow imports.** If a leaf still pulls in fifteen modules, it's still doing several jobs.
- **Don't invent abstraction.** If there's only one caller and no fork, leave it. Two near-identical blocks are the threshold, not one.
- **Don't trade one fork for another.** Splitting a component per state is only a win if the states really are separate; if three "states" differ by one line, a prop is the flatter answer.
- **Don't change behaviour to make the split easier.** If you spot a real bug, finish the refactor and report it separately.

## Output

1. Make the changes.
2. Run the project's typecheck/lint/tests and report the result honestly.
3. Summarise as a short table: file → what it now does → how many times it consults its main condition, before and after. Note anything you deliberately left alone and why.
