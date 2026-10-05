---
name: logo-generator
description: "Generate professional logos using AI (OpenAI image generation) through Claude Code with Deno CLI."
---
# Logo Generator

Generate professional logos using AI (OpenAI image generation) through Claude Code with Deno CLI.

## Requirements

- Deno 2.0+
- OpenAI API key with image generation access (`OPENAI_API_KEY`)
- Cost: $0.04 per standard logo, $0.16 per HD logo

## Quick Start

```bash
# Set API key
export OPENAI_API_KEY="sk-your-key-here"

# Start interactive session in Claude Code
!deno run --allow-all jsr:@logocli/logo-generator start
```

## Commands

| Command | Description |
|---------|-------------|
| `start` | Interactive session - Claude asks about company, generates diverse logos |
| `generate --company "Name" --prompt "description"` | Single logo generation |
| `batch --file logos.json --iteration N` | Batch generation from JSON file |
| `batch --help-examples` | Show JSON format examples |
| `config --api-key "sk-..."` | Set API key permanently |

## Workflow

1. Claude asks about your company (name, industry, style preferences)
2. Creates `iteration-1-batch.json` with diverse logo explorations
3. Generates 5-10 logos in `./logos/iteration-1/`
4. Asks which styles you prefer
5. Creates refined variations in `iteration-2/`, `iteration-3/`
6. Continues until you have the perfect logo

**Cost**: $0.80-$6.40 (20-40 logos across 3-4 iterations)
**Time**: 10-15 minutes
**Result**: 3-5 perfect logo options organized in folders

## Source

GitHub: https://github.com/frankdierolf/logo-generator
