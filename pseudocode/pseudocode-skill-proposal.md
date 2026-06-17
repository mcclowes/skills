# A Pseudocode Step for Claude Code: Rationale and Benchmark Design

*Proposal + evaluation plan. The claim under test is narrow and falsifiable: a distinct pseudocode phase improves the implementation of high-logic-complexity problems. The benchmark is designed to kill that claim if it's wrong.*

---

## 1. The argument in one paragraph

Pseudocode was never about syntax. It is a level-of-abstraction tool — a way to commit to the *shape* of a solution (control flow, data structures, invariants) before paying for the details. Historically its value scaled with two costs: being wrong in real code, and getting agreement before you wrote it. Code generation has collapsed the first cost to near zero for an LLM, which is why the step *feels* redundant. But the second cost inverted: when generation is cheap and **verification** is the bottleneck, an intermediate representation that is denser than prose, reviewable at a glance, and concrete exactly where prose hand-waves becomes *more* valuable, not less. The skill is a bet that this inversion is real and measurable.

## 2. Why this is not just "more planning"

Claude Code already plans. It writes prose outlines, TODO lists, spec comments, and chains of thought. So the honest framing isn't "planning vs no planning" — it's whether a *structured* intermediate (pseudocode) beats an *unstructured* one (prose) at equal compute. Natural language is more ambiguous than pseudocode, and it is most ambiguous precisely at the logic layer where the expensive bugs live: the loop boundary, the null case, the ordering, the invariant that must hold across a mutation. Pseudocode forces those to be named. Prose lets them stay implicit, then the model fills them in plausibly-but-wrongly at code-generation time.

If the skill has value, this is where it comes from. If it has *no* value, the most likely reason is that prose planning at equal token budget already captures everything pseudocode would — and the benchmark must be able to detect that outcome.

## 3. Where it should and shouldn't help

The discriminating variable is logic complexity, not task size.

- **Should help:** algorithms with subtle invariants, state machines, numerical methods, concurrency, anything where correct-looking code is routinely subtly wrong. (Concrete private examples: an Elo-style swing model, a bounded-trend forecasting formula, a Node state-machine library, a pipe-operator evaluator.)
- **Should not help — and may hurt:** CRUD endpoints, glue code, wiring, config. Here the code *is* the spec; a pseudocode step is pure latency and a cargo-culted ritual.

A skill that always pseudocodes is worse than no skill. The design goal is a step that triggers on complexity and stays out of the way otherwise. The benchmark must therefore include a low-complexity tier specifically to confirm the step is net-negative there, so the trigger logic can be tuned rather than assumed.

## 4. What the skill actually produces (operational definition)

Without a hard definition, "pseudocode" silently collapses into near-code and the eval measures nothing. The artifact must contain:

1. **Data structures and their invariants** — the shapes, and what must always be true of them.
2. **Control flow / algorithm steps** — the logic, language-agnostic.
3. **Edge cases and failure modes** — named explicitly, not discovered later.
4. **Interface contract** — inputs, outputs, error behaviour.

Hard constraints, enforceable by a linter:

- No target-language syntax, no real API/library calls.
- Must be reviewable by a human in under ~60 seconds. This constraint *is* the verification-surface thesis made operational.

## 5. Hypotheses

**Primary (H1).** On high-logic-complexity tasks, a distinct pseudocode step produces higher first-pass functional correctness than (a) direct implementation **and** (b) compute-matched prose planning. The "and (b)" is the part that makes this non-trivial.

**Secondary:**
- **H2 (review surface).** With the pseudocode artifact present, human reviewers detect seeded defects faster and more often than when reviewing equivalent code alone. This may hold *even if H1 fails* — the skill's value can live entirely on the review surface.
- **H3 (defect specificity).** Gains, where they exist, concentrate in logic/spec-misinterpretation defects, not syntax defects.
- **H4 (cost of misuse).** On low-complexity tasks, the step adds cost and latency with no correctness gain.

**Null / failure modes to take seriously:**
- **N1.** Gains vanish once compute is matched against prose planning (the step is just "more thinking" in a costume).
- **N2 (anchoring).** A wrong pseudocode plan locks in a wrong implementation more strongly than no plan, *increasing* catastrophic failures even if it raises the mean.

A benchmark that cannot return N1 or N2 is not measuring anything; it's a confirmation ritual.

## 6. Benchmark design

### 6.1 Task corpus

Three complexity tiers, ~50 tasks each (power permitting):

- **Tier H — high logic complexity:** invariant-heavy algorithms, state machines, numerical/financial methods, parsing, concurrency.
- **Tier M — mixed:** realistic features with a non-trivial core plus plumbing.
- **Tier L — low complexity:** CRUD, glue, config — the control tier for H4.

Each task ships with a **hidden functional test suite** (happy path) and a **separate adversarial edge-case suite** (boundaries, nulls, ordering, overflow, concurrency).

**Contamination control.** Public benchmark problems leak into training data and inflate everything uniformly. Mitigations: (1) mutate known problems structurally; (2) commission novel tasks; (3) **use a private set drawn from your own unpublished projects** — these are uncontaminated, genuinely logic-heavy, and you can grade them with authority. The private set is the most trustworthy signal here.

### 6.2 Experimental arms

Run every task through every arm; pair within task.

| Arm | Description | Controls for |
|---|---|---|
| **A. Direct** | Implement immediately | Baseline |
| **B. Pseudocode-first** | Produce §4 artifact, then implement | The treatment |
| **C. Prose-plan-first** | Natural-language plan, token-budget matched to B | "More compute" confound (kills/confirms N1) |
| **D. Test-first (TDD)** | Write tests, then implement | A rival structured intermediate |
| **E. Thinking-only** *(optional)* | Extended thinking, no externalised artifact | Whether externalisation matters at all |

Arm C is the load-bearing comparison. Without it, B beating A tells you almost nothing.

### 6.3 Metrics

**Model-side**
- `pass@1`, `pass@k` on the hidden functional suite.
- Edge-case suite pass rate (reported separately — the thesis predicts the gap shows up here).
- **Defect taxonomy** on failures: logic / off-by-one / boundary / spec-misinterpretation / syntax. Tests H3.
- Revisions-to-green (iterations to pass).
- Cost: tokens + wall-clock latency.

**Plan-quality mediator (for arms B, C, D)**
- Grade the artifact itself: correct approach? correct invariants?
- Mediation analysis: is implementation correctness explained by plan correctness?
- **Anchoring test (N2):** condition on plan-wrong cases — does a wrong plan produce *worse* outcomes than Arm A's no-plan baseline? If yes, the skill has a tail risk that the mean will hide.

**Human-review-side (tests H2)**
- Seed known defects into generated code. Give reviewers the code alone vs code + pseudocode artifact, blinded.
- Measure review time, defect-detection rate, and false-confidence (passing buggy code as clean).

### 6.4 Protocol

- **Pairing:** same task across arms; analyse paired differences, not group means.
- **Stochasticity:** m ≥ 5 samples per (task, arm); model task as a random effect (mixed-effects model).
- **Pre-registration:** fix H1 and the effect-size threshold *before* running. Otherwise you will find a significant result somewhere by accident.
- **Multiple comparisons:** correct for them; you have many secondary metrics.
- **Blinding:** graders and human reviewers blind to arm.
- **Report:** effect sizes with confidence intervals, not just p-values or win rates.

## 7. Threats to validity

- **Pseudocode collapses into code** → the abstraction-level linter (§4) is a measurement instrument, not a nicety. Audit a sample by hand.
- **Contamination** → private/mutated tasks; treat public-benchmark gains as suspect.
- **Grader overfit** → hidden + adversarial suites; spot-check autograder against human judgement.
- **Hawthorne effects** in human review → blind, counterbalance order.
- **Task-selection bias** → if you hand-pick tasks where pseudocode "obviously" helps, you've assumed the conclusion. Sample the tier by an independent complexity rubric, not by intuition about which way they'll go.

## 8. Decision criteria

**Ship the skill (complexity-gated) if** either:
- B beats **both** A and C on Tier-H correctness by the pre-registered effect size; **or**
- B fails on correctness but materially improves human-review metrics (H2) without raising catastrophic-failure rate (N2).

**Don't ship — or scope down — if:**
- Gains disappear once matched against prose (N1): the win was compute, not structure.
- Anchoring (N2) raises tail failures: the step is dangerous on exactly the hard tasks it targets.
- D (test-first) matches or beats B: a cheaper, already-familiar intermediate does the job, and you should build that instead.

The honest version of "success" is narrow: pseudocode earns a place *for high-complexity work, gated by a complexity trigger, when verification cost dominates generation cost.* Anything broader is the nostalgia talking.

## 9. Minimal first cut

Before the full study, run a cheap pilot to check for signal:

- 15–20 Tier-H tasks, weighted toward your private set.
- Three arms only: A (direct), B (pseudocode), C (prose-matched).
- Single blind grader, functional + edge suites, defect taxonomy by hand.
- Look for a B-over-C gap on edge-case pass rate. If it isn't visible at n≈20, it's unlikely to survive the compute control at scale — and you've saved yourself the human-review apparatus.

If the pilot shows nothing once C is in the room, that is itself a useful, publishable result: *structured intermediates don't beat prose at equal compute for current models* — which is a more interesting finding than another confirmation that planning helps.
