# Iteration 2 — findings (clean, serial grading)

## Headline: N1 holds — pseudocode shows no correctness gain over prose

On hard LiveCodeBench problems (the tier that gave arm A real headroom), plus-suite
pass rates: **A 85% · B 85% · C 82%**. The load-bearing comparison **B − C = +3 pts**
is well within noise (n = 3 samples/task, 11 tasks; most tasks are 0%/100% bimodal).
Across all tasks B − C = +2 pts. This is the proposal's **N1 null result**: a
structured intermediate does not beat compute-matched prose for this model.

It replicates across difficulty: iteration 1 (easy) saturated at ~100% for all arms;
iteration 2 (hard) lands at ~85% for all arms. No arm separation that survives noise.

## Pseudocode is *dominated* by prose on cost

Arm B wrote **510 words** on hard tasks vs arm C's **355** — and got the same
correctness. So B is not merely "no better"; it costs ~45% more output for an equal
result. The skill is not earning its token budget as a correctness tool.

## Weak, noisy secondary signals

- **Externalizing a plan helped over direct on 2 tasks** (abc325_e, abc324_d:
  A 67% → B/C 100%). But B and C were interchangeable — the win, where it exists,
  is "write a plan", not "write *pseudocode* specifically".
- **No credible anchoring (N2).** The one apparent case (abc319_e: A 100%, B 33%,
  C 0%) is a **TLE artifact**, not anchoring: those solutions run near the time limit
  and the planned arms' solutions were marginally slower, failing on large hidden
  inputs that the faster direct solution cleared. Confirmed by hand — the direct
  solution there also takes >10s on some cases.

## Robust, actionable: artifact discipline degrades under difficulty

- Lint pass: **16/45**. Mean code-tells 0.84 (up from 0.12 in iter-1).
- Arm-B artifacts ballooned to **459–732 words** on hard tasks — far past the
  "reviewable in ~60s / < 60 lines" budget the skill asks for.
- This is the "pseudocode collapses toward code" threat (proposal §7) materializing
  exactly when the task is hard — i.e. when the skill is meant to help most.

## Methodological lessons (for any future iteration)

1. **Never grade timed solutions in parallel with wall-clock timeouts.** CPU
   contention across workers produces spurious TLEs. The first parallel pass reported
   a bogus B − C = −9 pts; serial re-grading erased it. (See
   `benchmark_PARALLEL_CONTAMINATED.*` for the corrupted run.)
2. **Competitive-programming tasks confound this thesis.** They test algorithmic
   *insight* and are *performance*-sensitive in Python; the thesis is about logic
   *correctness* under subtle invariants. TLE noise pollutes the signal.

## The thesis's true sweet spot was never tested

Neither corpus hit the claim's strongest form: tasks that are **edge-case-subtle**
(invariant-heavy, where correct-looking code is silently wrong) **and** hard enough
that the model fails them without a plan. HumanEval+ was too easy; LCB is the wrong
kind of hard; the novel tasks were edge-dense but algorithmically trivial (100%
everywhere). Building that corpus — or testing the human-review hypothesis (H2),
where the skill's value may actually live — is the real next step.

## Decision (per proposal §8)

> "Gains disappear once matched against prose (N1): the win was compute, not
> structure → Don't ship — or scope down."

On the evidence so far: **do not ship pseudocode as a correctness tool.** Defensible
scoped version: "for hard logic, externalize a *brief* plan (prose or pseudocode),
gated by complexity" — which is weaker and not pseudocode-specific. The skill's
remaining upside is the untested review surface (H2).
