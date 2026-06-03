# AI-aware code structure

How to organise code across files when an AI coding agent is one of the readers. Splits, file size, and co-location decisions, recalibrated for the fact that agents are reluctant to read adjacent files.

## Structure

- `SKILL.md` - Main skill instructions: the three-reader framing, the "understood in isolation?" test, and the core heuristics
- `evals/evals.json` - Test prompts for verifying the skill triggers and gives the right guidance

## Usage

This skill is automatically discovered by Claude when relevant to the task.
