# benchmarking

Benchmark workspaces for the skills in this repo, kept under version control as a
record of skill quality over time. Each `<skill-name>-workspace/` holds:

- `fixtures/` — eval input data (source-like, reused across runs)
- `iteration-N/` — one benchmark run: per-eval outputs, gradings, timings, and the
  aggregated `benchmark.md` / `benchmark.json` summaries
- `skill-snapshot/` — the pre-edit skill copy used as the baseline in Improve mode

## Convention

The `skill-creator` tooling generates a workspace as a **sibling of the skill**
(`skills/<name>/` → `skills/<name>-workspace/`) by default. After a run, move the
workspace here to keep `skills/` to source only:

```sh
git mv skills/<name>-workspace benchmarking/<name>-workspace
```

Eval configs reference fixtures by relative path. A skill's `evals/evals.json` reaches
fixtures here via `../../benchmarking/<name>-workspace/fixtures/...` (relative to the
skill directory). Update those paths if you relocate a workspace.
