# Pseudocode benchmark — iteration-2

Arms: **A** direct · **B** pseudocode-first · **C** prose-plan (compute-matched). 3 samples/task. 135 total runs.

Base = happy/sample suite · Plus = hidden adversarial suite. The load-bearing test is **B vs C on Plus**: does *structure* beat *prose at equal compute*?


## LiveCodeBench hard (stdio)

| Arm | n | Base pass | Plus pass | Edge gap | Artifact words |
|---|---|---|---|---|---|
| A · direct | 33 | 88% | 85% | 3% | — |
| B · pseudocode | 33 | 91% | 85% | 6% | 510 |
| C · prose-matched | 33 | 91% | 82% | 9% | 355 |

_Headline (Plus): **B−A = +0 pts**, **B−C = +3 pts** (load-bearing). Compute match: B≈510w vs C≈355w._

## Novel contamination-free (functional)

| Arm | n | Base pass | Plus pass | Edge gap | Artifact words |
|---|---|---|---|---|---|
| A · direct | 12 | 100% | 100% | 0% | — |
| B · pseudocode | 12 | 100% | 100% | 0% | 318 |
| C · prose-matched | 12 | 100% | 100% | 0% | 288 |

_Headline (Plus): **B−A = +0 pts**, **B−C = +0 pts** (load-bearing). Compute match: B≈318w vs C≈288w._

## All tasks

| Arm | n | Base pass | Plus pass | Edge gap | Artifact words |
|---|---|---|---|---|---|
| A · direct | 45 | 91% | 89% | 2% | — |
| B · pseudocode | 45 | 93% | 89% | 4% | 459 |
| C · prose-matched | 45 | 93% | 87% | 7% | 337 |

_Headline (Plus): **B−A = +0 pts**, **B−C = +2 pts** (load-bearing). Compute match: B≈459w vs C≈337w._

## Arm-B artifact health

- pseudocode.md present: 45/45 · passes lint: 16/45 · mean code-tells: 0.84

## Per-task Plus pass (anchoring watch — B << A flags N2)

| Task | Source | A | B | C |
|---|---|---|---|---|
| lcb/abc325_d | livecodebench | 100% | 100% | 100% |
| lcb/abc325_e | livecodebench | 67% | 100% | 100% |
| lcb/abc324_d | livecodebench | 67% | 100% | 100% |
| lcb/abc324_e | livecodebench | 100% | 100% | 100% |
| lcb/abc323_d | livecodebench | 100% | 100% | 100% |
| lcb/abc323_e | livecodebench | 100% | 100% | 100% |
| lcb/abc322_e | livecodebench | 100% | 100% | 100% |
| lcb/abc320_e | livecodebench | 100% | 100% | 100% |
| lcb/abc319_e | livecodebench | 100% | 33% | 0% |
| lcb/abc318_e | livecodebench | 100% | 100% | 100% |
| lcb/abc315_e | livecodebench | 0% | 0% | 0% |
| novel/token_bucket | novel | 100% | 100% | 100% |
| novel/elo_swing | novel | 100% | 100% | 100% |
| novel/eval_expr | novel | 100% | 100% | 100% |
| novel/merge_weighted_intervals | novel | 100% | 100% | 100% |
