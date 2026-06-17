# Pseudocode benchmark — iteration-1

Arms: **A** direct · **B** pseudocode-first · **C** prose-plan (compute-matched). 3 samples/task. 135 total runs.

Two suites per task: **base** (happy path) and **plus** (adversarial edge cases, from EvalPlus / hand-authored). The thesis predicts arm B's advantage shows up on the **plus** suite and on the **edge gap** (base − plus), concentrated in **Tier H**.


## Tier H — high logic complexity (the thesis tier)

| Arm | n | Base pass | Plus pass | Edge gap | Artifact words |
|---|---|---|---|---|---|
| A · direct | 39 | 100% | 97% | 3% | — |
| B · pseudocode | 39 | 100% | 100% | 0% | 258 |
| C · prose-matched | 39 | 100% | 100% | 0% | 281 |

## Tier L — trivial control (skill should NOT help)

| Arm | n | Base pass | Plus pass | Edge gap | Artifact words |
|---|---|---|---|---|---|
| A · direct | 6 | 100% | 100% | 0% | — |
| B · pseudocode | 6 | 100% | 100% | 0% | 48 |
| C · prose-matched | 6 | 100% | 100% | 0% | 239 |

## Headline (Tier H, plus suite)

- **B vs A** (pseudocode vs direct): 100% − 97% = **+3 pts**
- **B vs C** (pseudocode vs compute-matched prose — the load-bearing test): 100% − 100% = **+0 pts**
- Artifact compute match: B ≈ 258 words vs C ≈ 281 words

## Arm-B artifact health (linter)

- pseudocode.md present: 41/45
- passes abstraction-level lint: 27/41
- mean code-tells (lower = more language-agnostic): 0.12

## Per-task plus pass (anchoring watch — B notably below A flags N2)

| Task | Tier | A | B | C |
|---|---|---|---|---|
| HumanEval/108 | H | 100% | 100% | 100% |
| HumanEval/109 | H | 100% | 100% | 100% |
| HumanEval/126 | H | 100% | 100% | 100% |
| HumanEval/129 | H | 100% | 100% | 100% |
| HumanEval/147 | H | 100% | 100% | 100% |
| HumanEval/160 | H | 100% | 100% | 100% |
| HumanEval/100 | H | 100% | 100% | 100% |
| HumanEval/163 | H | 67% | 100% | 100% |
| HumanEval/115 | H | 100% | 100% | 100% |
| HumanEval/23 | L | 100% | 100% | 100% |
| HumanEval/53 | L | 100% | 100% | 100% |
| novel/token_bucket | H | 100% | 100% | 100% |
| novel/elo_swing | H | 100% | 100% | 100% |
| novel/eval_expr | H | 100% | 100% | 100% |
| novel/merge_weighted_intervals | H | 100% | 100% | 100% |
