# Iteration 1 — findings

## Headline: ceiling effect, hypothesis untestable at this difficulty

Opus 4.8 solves the corpus in all three arms. Tier-H plus-suite pass rates:
A·direct 97%, B·pseudocode 100%, C·prose 100%. The load-bearing comparison
(B vs C) is +0 pts — but arm A is already at ~ceiling, so there is no headroom
to detect a structure-over-prose effect. Per the proposal, a benchmark that
cannot return N1/N2 is not yet measuring the claim. HumanEval+ is contaminated
and too easy for this model even at its hard end.

## Signals that ARE informative (independent of ceiling)

- **Complexity gating works (H4).** Arm B produced no pseudocode on the Tier-L
  controls: HumanEval/53 (a+b) skipped all 3 runs; strlen skipped 1/3. The skill
  stays out of the way on trivial work.
- **Artifacts are real pseudocode.** Mean 0.12 code-tells across 41 arm-B
  artifacts; language-agnostic as intended.
- **Compute match between B and C holds.** B ≈ 258 words vs C ≈ 281 words on
  Tier H — so any future B-vs-C gap is structure, not "more thinking".

## Linter caveats to fix

- Section detection is keyword-based and over-strict: several 4/4 artifacts
  scored 3/4 because a section was present semantically but not by keyword.
- A couple of false-positive code-tells on tuple notation like (start, end, w).

## Next: iteration 2 must raise task difficulty

Need contamination-controlled, genuinely hard *logic* tasks that pull arm A
well below 100% (target ~50-70%) so B vs C can separate. Candidate sources:
LiveCodeBench (hard, time-stamped), APPS competition tier, harder novel tasks.
