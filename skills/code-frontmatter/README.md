# Code Frontmatter

Context-efficient codebase navigation and documentation using structured frontmatter headers. A short YAML header at the top of each file describes its purpose and related files, so you can map a tree from headers (~50 tokens each) instead of reading every file (~1500 tokens each).

## Structure

- `SKILL.md` - Main skill instructions: the authoring vs navigating modes and the common-case workflow
- `SPECIFICATION.md` - Full frontmatter schema reference
- `scripts/frontmatter.py` - Bundled script to `generate`, `index`, and validate frontmatter
- `python-example.py` - Example of a frontmatter header in Python
- `typescript-example.ts` - Example of a frontmatter header in TypeScript
- `evals/evals.json` - Test prompts for verifying the skill triggers and behaves correctly

## Usage

This skill is automatically discovered by Claude when relevant to the task.
