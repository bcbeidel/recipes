# recipes

A personal recipe vault for meal planning, designed to be opened in [Obsidian](https://obsidian.md).

Recipes are organized by meal type (dinner, breakfast, lunch, sides,
desserts, appetizers, basics) with frontmatter for cuisine, dietary
tags, and cooking time. Dataview queries in `_index.md` surface recipes
by category, dietary restriction, or weeknight-friendliness to support
week-by-week meal planning.

## Prerequisites

- [Obsidian](https://obsidian.md) (any recent version)
- [Dataview](https://github.com/blacksmithgu/obsidian-dataview)
  community plugin — required for the dynamic queries in `_index.md`

## Installation

Clone the repo and open the directory as an Obsidian vault:

```bash
git clone https://github.com/bbeidel/recipes.git
```

In Obsidian: **Open folder as vault** → select the cloned directory.

Then enable Dataview: **Settings → Community plugins → Browse → "Dataview" → Install → Enable**.

## Usage

Open `_index.md` to browse the vault. The index renders Dataview
queries that group recipes by meal type, cuisine, dietary tag, and
cooking time.

Individual recipes live under the meal-type directories (`dinner/`,
`breakfast/`, etc.). Each recipe is a markdown file with frontmatter:

```yaml
---
meal-type: dinner
cuisine: italian
dietary: [vegetarian]
cooking-time: 30 minutes
cooking-time-minutes: 30
difficulty: easy
---
```

## Tooling

This repo uses [bcbeidel/toolkit](https://github.com/bcbeidel/toolkit)
for Claude Code scaffolding — README, `RESOLVER.md`, and other
supporting files are generated and audited via toolkit skills.
Additional tooling will be added over time.

See `AGENTS.md` for working agreements and `RESOLVER.md` for context-routing rules.

## Troubleshooting

**Problem:** The `_index.md` page shows code blocks instead of rendered recipe lists.
**Cause:** The Dataview plugin is not installed or not enabled.
**Fix:** Install and enable Dataview under **Settings → Community plugins**.

## License

All rights reserved — personal use only, not licensed for
redistribution. See [LICENSE](LICENSE) for the full terms, including
how this applies to recipes adapted from cited sources.
