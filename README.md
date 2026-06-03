# Claude skills

A general-purpose collection of [agent skills](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code and Claude.ai.

## Installation

```bash
npx skills add mcclowes/skills
```

Install specific skills only:

```bash
npx skills add mcclowes/skills --skill api-design
```

Install globally (available across all projects):

```bash
npx skills add mcclowes/skills -g
```

Preview available skills before installing:

```bash
npx skills add mcclowes/skills --list
```

## Available skills

| Skill | Description |
|-------|-------------|
| **api-design** | Design and review developer-friendly HTTP API responses — a unified `issues` array for consistent error and warning handling, with field reference and React consumption examples |

## Alternative installation methods

### As a Claude Code plugin

```bash
claude mcp add-json mcclowes-skills '{"type":"stdio","command":"npx","args":["-y","claude-skills-cli","serve","https://raw.githubusercontent.com/mcclowes/skills/main/.claude-plugin/marketplace.json"]}'
```

### With OpenSkills

```bash
npm i -g openskills
openskills install mcclowes/skills
```

### Manual

Copy skill directories from `skills/` to your `.claude/skills/` folder.

## Ensuring reliable skill activation

By default, Claude Code may not always activate skills when relevant. For more reliable activation, set up the **forced eval hook**:

```bash
./setup-hook.sh
```

Or manually:

1. Copy the hook: `cp hooks/skill-activation-forced-eval.sh .claude/hooks/`
2. Make executable: `chmod +x .claude/hooks/skill-activation-forced-eval.sh`
3. Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/skill-activation-forced-eval.sh"
          }
        ]
      }
    ]
  }
}
```

4. Restart Claude Code.

See [this blog post](https://scottspence.com/posts/how-to-make-claude-code-skills-activate-reliably#the-winner-sort-of-forced-eval-hook) for details.

## License

See [LICENCE](LICENCE) file for details.

## Contributing

Contributions welcome — please feel free to submit issues or pull requests.
