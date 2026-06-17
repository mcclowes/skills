#!/usr/bin/env python3
"""Emit the pilot workflow script with the task list embedded inline.

The workflow script runs in a sandbox with no filesystem access, so we bake the
task prompts into the script rather than reading the corpus at run time. Each
agent writes to a deterministic path; grading happens locally afterward.
"""
import json

WS = "/Users/mcclowes/Development/mcclowes/skills/benchmarking/pseudocode-workspace/iteration-1"
SKILL = "/Users/mcclowes/Development/mcclowes/skills/skills/pseudocode/SKILL.md"

corpus = json.load(open("/Users/mcclowes/Development/mcclowes/skills/benchmarking/pseudocode-workspace/fixtures/corpus.json"))
tasks = [{
    "task_id": t["task_id"],
    "dir": t["task_id"].replace("/", "__"),
    "prompt": t["prompt"],
} for t in corpus]

script = '''export const meta = {
  name: 'pseudocode-pilot',
  description: 'Generate benchmark solutions: 15 tasks x 3 arms (direct/pseudocode/prose) x 3 samples = 135 runs',
  phases: [{ title: 'Generate' }],
}

const WS = ''' + json.dumps(WS) + '''
const SKILL = ''' + json.dumps(SKILL) + '''
const TASKS = ''' + json.dumps(tasks) + '''
const SAMPLES = [1, 2, 3]

function promptFor(arm, t, s) {
  const base = WS + '/' + t.dir + '/' + arm + '/run-' + s
  const TASK = '\\n\\nTASK:\\n' + t.prompt + '\\n\\nReport only the path(s) you wrote.'
  if (arm === 'A_direct') {
    return 'Implement a Python function. Write ONLY the complete function plus any needed imports to this exact file path:\\n'
      + base + '/solution.py\\n'
      + 'Do not write tests, a main block, or explanation. Create parent directories if needed.' + TASK
  }
  if (arm === 'B_pseudocode') {
    return 'You have access to a skill at ' + SKILL + ' — read it and follow it for this task.\\n'
      + 'Task: implement the Python function below.\\n'
      + 'If the skill directs you to write a pseudocode plan, write that plan to:\\n' + base + '/pseudocode.md\\n'
      + 'Then write the complete implementation (function + any imports only, no tests, no main block) to:\\n' + base + '/solution.py\\n'
      + 'Create parent directories if needed.' + TASK
  }
  // C_prose
  return 'First write a thorough natural-language plan (roughly 150-250 words) describing your approach to the task below: the data involved, the algorithm steps, the edge cases you will handle, and the function\\'s input/output contract. Write the plan to:\\n'
    + base + '/plan.md\\n'
    + 'Then write the complete implementation (function + any imports only, no tests, no main block) to:\\n' + base + '/solution.py\\n'
    + 'Create parent directories if needed.' + TASK
}

const jobs = []
for (const t of TASKS) {
  for (const s of SAMPLES) {
    for (const arm of ['A_direct', 'B_pseudocode', 'C_prose']) {
      jobs.push({ arm, t, s })
    }
  }
}
log('spawning ' + jobs.length + ' generation runs')

const results = await parallel(jobs.map(j => () =>
  agent(promptFor(j.arm, j.t, j.s), {
    label: j.arm + ':' + j.t.dir + ':r' + j.s,
    phase: 'Generate',
  }).then(() => ({ ok: true, arm: j.arm, task: j.t.task_id, s: j.s }))
))

const ok = results.filter(Boolean).filter(r => r.ok).length
return { generated: ok, total: jobs.length }
'''

out = "/Users/mcclowes/Development/mcclowes/skills/benchmarking/pseudocode-workspace/harness/pilot_workflow.js"
with open(out, "w") as f:
    f.write(script)
print("wrote", out, "with", len(tasks), "tasks,", len(tasks) * 3 * 3, "total runs")
