#!/usr/bin/env python3
"""Emit the iteration-2 workflow: stdio (LCB) + functional (novel) tasks x 3 arms x 3 samples."""
import json

WS = "/Users/mcclowes/Development/mcclowes/skills/benchmarking/pseudocode-workspace/iteration-2"
SKILL = "/Users/mcclowes/Development/mcclowes/skills/skills/pseudocode/SKILL.md"

corpus = json.load(open("/Users/mcclowes/Development/mcclowes/skills/benchmarking/pseudocode-workspace/fixtures/corpus_iter2.json"))
tasks = [{"task_id": t["task_id"], "dir": t["task_id"].replace("/", "__"),
          "prompt": t["prompt"], "harness": t["harness"]} for t in corpus]

script = '''export const meta = {
  name: 'pseudocode-pilot-2',
  description: 'Iteration 2: 15 hard tasks (LCB stdio + novel functional) x 3 arms x 3 samples = 135 runs',
  phases: [{ title: 'Generate' }],
}

const WS = ''' + json.dumps(WS) + '''
const SKILL = ''' + json.dumps(SKILL) + '''
const TASKS = ''' + json.dumps(tasks) + '''
const SAMPLES = [1, 2, 3]

function deliverable(harness) {
  return harness === 'stdio'
    ? 'Write a COMPLETE Python program that reads from standard input and writes the answer to standard output'
    : 'Write ONLY the complete Python function plus any needed imports'
}
function taskHeader(harness) {
  return harness === 'stdio' ? '\\n\\nPROBLEM:\\n' : '\\n\\nTASK:\\n'
}

function promptFor(arm, t, s) {
  const base = WS + '/' + t.dir + '/' + arm + '/run-' + s
  const D = deliverable(t.harness)
  const TASK = taskHeader(t.harness) + t.prompt + '\\n\\nReport only the path(s) you wrote.'
  if (arm === 'A_direct') {
    return D + ' to this exact file path:\\n' + base + '/solution.py\\n'
      + 'Do not write tests or explanation. Create parent directories if needed.' + TASK
  }
  if (arm === 'B_pseudocode') {
    return 'You have access to a skill at ' + SKILL + ' — read it and follow it for this task.\\n'
      + 'Task below. If the skill directs you to write a pseudocode plan, write it to:\\n' + base + '/pseudocode.md\\n'
      + 'Then ' + D.charAt(0).toLowerCase() + D.slice(1) + ' to:\\n' + base + '/solution.py\\n'
      + 'Create parent directories if needed.' + TASK
  }
  return 'First write a thorough natural-language plan (roughly 150-250 words) of your approach to the task below: the data, the algorithm steps, the edge cases you will handle, and the input/output contract. Write the plan to:\\n'
    + base + '/plan.md\\n'
    + 'Then ' + D.charAt(0).toLowerCase() + D.slice(1) + ' to:\\n' + base + '/solution.py\\n'
    + 'Create parent directories if needed.' + TASK
}

const jobs = []
for (const t of TASKS) for (const s of SAMPLES) for (const arm of ['A_direct','B_pseudocode','C_prose']) {
  jobs.push({ arm, t, s })
}
log('spawning ' + jobs.length + ' generation runs')
const results = await parallel(jobs.map(j => () =>
  agent(promptFor(j.arm, j.t, j.s), { label: j.arm + ':' + j.t.dir + ':r' + j.s, phase: 'Generate' })
    .then(() => ({ ok: true }))
))
return { generated: results.filter(Boolean).length, total: jobs.length }
'''

out = "/Users/mcclowes/Development/mcclowes/skills/benchmarking/pseudocode-workspace/harness/pilot_workflow2.js"
open(out, "w").write(script)
print("wrote", out, "with", len(tasks), "tasks,", len(tasks) * 9, "runs")
