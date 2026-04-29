---
name: Recipe-card vault audit baseline
description: Tier-1 audit findings as of feat/recipe-card-skill-pair landing — input for the follow-on repair plan.
type: notes
related:
  - .plans/2026-04-29-recipe-card-skill-pair.plan.md
---

# Vault audit baseline (Task 6)

Run command:

```bash
for d in dinner breakfast lunch sides desserts appetizers basics; do
  .claude/skills/check-recipe-card/scripts/audit_recipe_card.py \
    --folder "$d"
done
```

Raw combined JSON: `/tmp/recipe-card-audit.json` (gitignored — not
committed; regenerate from the command above when needed).

## Vault-wide totals

- **167 files audited** across the seven recipe folders.
- **161 findings.**
- **150 description-bug findings** (`description-not-placeholder` +
  `description-not-first-ingredient`). Validation criterion ≥100 met.

## By folder

| Folder | Audited | Findings |
|---|---:|---:|
| dinner | 100 | 96 |
| breakfast | 16 | 14 |
| lunch | 4 | 4 |
| sides | 11 | 13 |
| desserts | 10 | 9 |
| appetizers | 8 | 7 |
| basics | 18 | 18 |

## By dimension (vault-wide)

| Dimension | Count |
|---|---:|
| description-not-first-ingredient | 148 |
| url-present | 4 |
| required-fields-present | 4 |
| description-not-placeholder | 2 |
| body-has-ingredients | 2 |
| body-has-preparation | 1 |

## Concrete structural breakage (rare findings)

These are the files the follow-on repair plan should touch
hands-on — auto-fix paths in `repair-playbook.md` are weaker for
these dimensions.

**Missing `## Ingredients` heading**

- `dinner/tofu-with-broccoli-and-spicy-peanut-sauce.md`
- `dinner/whatever-youve-got-fried-rice.md`

**Missing `## Preparation` heading**

- `dinner/whatever-youve-got-fried-rice.md`

**Missing required fields**

- `dinner/mississippi-roast.md` — `cooking-time-minutes`
- `dinner/penne-with-brussels-sprouts-chili-and-panchetta.md` —
  `cooking-time-minutes`
- `basics/tomato-tortellini-soup.md` — `cooking-time-minutes`
- `sides/watermelon-salad-with-feta-and-mint.md` — `url`

**`url:` not http(s)://**

- `dinner/chicken-dumpling.md`
- `dinner/coconut-curry-ramen-and-veggie-noodle-soup.md`
- `dinner/tofu-with-broccoli-and-spicy-peanut-sauce.md`

## Follow-on

The dominant signal (148 `description-not-first-ingredient` plus 2
placeholder) is mechanically auto-fixable per
`repair-playbook.md`'s Tier-1 entry: set `description: null` and
add `needs-review`. A follow-on plan can sweep this in one batch and
optionally enable the Tier-2 `description-is-summary` propose-diff
loop to generate real summaries.
