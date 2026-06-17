# pseudocode-workspace

Benchmark for the [`pseudocode`](../../skills/pseudocode/) skill. The skill is a
bet that, now that generating code is cheap and *verifying* it is the bottleneck,
a structured language-agnostic plan beats both direct implementation and
unstructured prose planning on logic-heavy tasks. This workspace is built to
**kill that claim if it's wrong**, following `pseudocode-skill-proposal.md`.

## The claim under test

The load-bearing comparison is **arm B vs arm C**, not B vs A. If pseudocode only
beats direct implementation (A) but not compute-matched prose (C), the win was
"more thinking," not structure — and the skill isn't pulling its weight.

## Arms

| Arm | What it does | Controls for |
|---|---|---|
| **A · direct** | implement immediately | baseline |
| **B · pseudocode** | follow the skill (plan, then code) | the treatment |
| **C · prose-matched** | ~150-250 word prose plan, then code | the "more compute" confound |

Every task runs through every arm, 3 samples each.

## Suites: base vs plus

Each task ships two test suites, graded separately:
- **base** — happy path / sample cases.
- **plus** — hidden adversarial edge cases.

The thesis predicts arm B's advantage (if any) concentrates on **plus** and on the
**edge gap** (base − plus): the off-by-one, the null, the boundary that prose
buries under "handle the edge cases."

## Corpus

- `fixtures/corpus.json` — iteration 1: HumanEval/HumanEval+ logic-heavy subset +
  novel tasks + Tier-L controls. **Result: saturated** — too easy for the model,
  no headroom. See `iteration-1/FINDINGS.md`.
- `fixtures/corpus_iter2.json` — iteration 2: hard LiveCodeBench problems
  (AtCoder ABC D/E, stdio harness) for headroom + the 4 novel contamination-free
  tasks (functional harness) as a clean anchor.

### Contamination note

HumanEval is contaminated; LiveCodeBench's 2023 contest dates predate the model's
training cutoff, so absolute pass rates may be inflated. The **relative** arm
comparison (B vs C at matched compute) is the trustworthy signal. The novel tasks
are uncontaminated by construction.

## Harness (`harness/`)

| File | Role |
|---|---|
| `lint_pseudocode.py` | abstraction-level linter: verifies arm-B artifacts are language-agnostic (no target syntax / API calls), cover the 4 required sections, and are reviewable (<60 lines). Also bundled with the skill. |
| `grade.py` | functional grader: runs base/plus `check(candidate)` suites in a sandboxed subprocess. |
| `grade_stdio.py` | stdio grader: feeds stdin, compares stdout (line-rstripped) for LCB programs. |
| `aggregate_pilot.py` | iteration-1 aggregation. |
| `aggregate_iter2.py` | iteration-2 aggregation, dispatches by task `harness` field. |
| `build_corpus_*.py` | reproducible corpus builders (HumanEval, LCB, novel, iter2). |
| `gen_workflow*.py` | emit the generation workflow scripts. |
| `pilot_workflow*.js` | the workflows: fan out task×arm×sample generation across agents. |

## Reproduce an iteration

```sh
# 1. (re)build corpus — see build_corpus_*.py
# 2. generate solutions: launch harness/pilot_workflow2.js via the Workflow tool
# 3. grade + aggregate:
python harness/aggregate_iter2.py iteration-2 fixtures/corpus_iter2.json
# 4. read iteration-2/benchmark.md
```

Generation runs through the Workflow tool (one agent per task×arm×sample);
grading is pure local computation, so no agent tokens are spent on it.
