# Pseudocode skill — benchmark report

**Question.** Does a distinct pseudocode step improve the implementation of
high-logic-complexity problems — specifically, does it beat *compute-matched prose
planning*, not just direct implementation? (Full design:
`../../skills/pseudocode/` and the original `pseudocode-skill-proposal.md`.)

**Answer, on the evidence so far: no.** Across two iterations and 270 model runs
(Opus 4.8), pseudocode-first shows no correctness advantage over a prose plan of
matched length, and costs more tokens for the same result. This is the proposal's
pre-registered **N1** outcome ("the win was compute, not structure"). It is a clean
negative result, with important caveats about what was *not* tested.

---

## What was built

- **The skill** (`skills/pseudocode/`): complexity-gated (decides whether to
  pseudocode at all — a step on trivial work is worse than none), produces a
  four-part artifact (data + invariants, control flow, edge cases, interface
  contract), with abstraction-level constraints, plus `lint_pseudocode.py`, a
  linter that checks the artifact is language-agnostic and reviewable.
- **A real benchmark** (`pseudocode-workspace/`): three arms — A (direct),
  B (pseudocode), C (compute-matched prose) — over tasks with separate happy-path
  (base) and adversarial (plus) test suites, graded by executing code against hidden
  tests. Corpus drawn from HumanEval+, LiveCodeBench-hard, and novel
  contamination-free tasks.

## Results

| Plus-suite pass@1 | A · direct | B · pseudocode | C · prose | B − C |
|---|---|---|---|---|
| Iteration 1 — HumanEval+ (easy) | 97% | 100% | 100% | 0 |
| Iteration 2 — LiveCodeBench hard | 85% | 85% | 82% | +3 |
| Iteration 2 — novel (contamination-free) | 100% | 100% | 100% | 0 |

- **B vs C is within noise** (n = 3 samples × 11 hard tasks; pass is bimodal per
  task). No separation that survives.
- **Pseudocode is dominated on cost**: 510 words vs prose's 355 for equal
  correctness on hard tasks.
- **Externalizing *a* plan helped over direct on 2 hard tasks** — but prose and
  pseudocode were interchangeable there.
- **Gating works**: in iteration 1 the skill correctly skipped pseudocode on the
  trivial control tasks.
- **Artifact discipline degrades under difficulty**: linter pass fell to 16/45;
  artifacts ballooned to 460–730 words, past the "reviewable in ~60s" budget. The
  "pseudocode collapses into code" failure mode, arriving exactly when the task is
  hard.

## What this does and does not establish

**Establishes** (for this model, these tasks): a structured plan is not worth more
than an equally-long prose plan for first-pass functional correctness, and the
pseudocode form specifically costs more.

**Does not establish** — the three open threads:
1. **The thesis's true sweet spot was never tested.** The claim is about
   edge-case-subtle logic where correct-looking code is silently wrong. HumanEval+
   was too easy; LiveCodeBench tests algorithmic insight and is performance-sensitive
   (TLE confounds correctness in Python); the novel tasks were edge-dense but
   algorithmically trivial. The corpus that would truly stress H1 — hard *and*
   edge-subtle *and* not performance-bound — remains unbuilt.
2. **The review surface (H2) is untested.** The proposal's secondary claim is that
   the artifact helps a *human reviewer* catch defects faster, which can hold even if
   H1 fails. Not measured.
3. **No credible anchoring (N2).** The one alarming-looking case was a TLE artifact,
   not the model being misled.

## Methodological lessons (worth keeping)

- **Never grade timed solutions in parallel with wall-clock timeouts.** CPU
  contention causes spurious TLEs; the first parallel pass produced a bogus
  B − C = −9 pts that vanished on serial re-grading. The corrupted run is preserved
  as `iteration-2/benchmark_PARALLEL_CONTAMINATED.*`.
- **Competitive-programming tasks are a poor substrate for a *logic-correctness*
  thesis** — they test insight and reward performance, both confounds.

## Recommendation

Per the proposal's decision criteria (§8), N1 → do not ship pseudocode as a
correctness tool. The defensible scoped-down version is weaker and not
pseudocode-specific: *for hard logic, externalize a brief plan (prose or pseudocode),
gated by complexity.* The real upside that remains is the untested review surface.
If the work resumes, the highest-value next step is building the true sweet-spot
corpus (open thread 1) or testing H2 (open thread 2).

## Map

- `iteration-1/` — HumanEval+ run; `iteration-1/FINDINGS.md` (ceiling effect).
- `iteration-2/` — hard run; `iteration-2/FINDINGS.md` (clean N1); `benchmark.md`
  (clean), `benchmark_PARALLEL_CONTAMINATED.md` (the grading-bug run, kept as a
  cautionary record).
- `harness/` — graders, linter, aggregators, corpus builders, workflows. Reproduce
  per `README.md`.
