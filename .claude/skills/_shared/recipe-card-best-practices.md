---
name: Recipe-Card Best Practices
description: Authoring guide for recipe-cards — single markdown documents that record cited recipes for this Obsidian vault. Referenced by build-recipe-card and check-recipe-card.
---

# Recipe-Card Best Practices

## What a Good Recipe-Card Does

A recipe-card is a single markdown document that captures one recipe
from a named, cited source so it can be cooked from later, queried by
Dataview from `_index.md`, and cross-referenced from other cards via
wikilinks. It is not a meal plan, a how-to article, or a generated
invention — it is a faithful transcription with metadata.

A good card earns its place when:

- The reader can cook from it without returning to the source.
- The frontmatter answers Dataview queries in `_index.md` (meal-type,
  cuisine, dietary, cooking-time-minutes).
- The source is named and credible enough to trust unverified.
- Wikilinks to component recipes (basics) resolve.

## Anatomy

```markdown
---
description: <one-sentence summary of what the dish is>
aliases:
  - "<Title Case Display Name>"
tags:
  - recipe
  - <meal-type tag>
  - <other tags>
meal-type: dinner|breakfast|lunch|side|dessert|appetizer
difficulty: easy|medium|hard|project
cuisine: <cuisine or null>
dietary: [<vegetarian|vegan|gluten-free|...>]
cooking-time: "<human-readable>"
cooking-time-minutes: <integer>
servings: <human-readable>
url: <citation URL>
rating: <0-5 or null>
last-cooked: <YYYY-MM-DD>
---

## Ingredients

- <quantity + ingredient + prep>
- <...>

(optional sub-headings for multi-component dishes:)

FOR THE CRUST:

- <bullet>

For the Sauce

- <bullet>

---

## Preparation

1. <imperative step>
2. <imperative step>
...

(optional trailing personal notes block:)

> [!important]
> <personal note>
```

**Filename**: kebab-case stem matching the alias, ASCII apostrophes
only (curly apostrophes are stripped — see
`scripts/transform_recipes.py:strip_curly`).

**Folder**: derived from `meal-type` per RESOLVER.md filing table.
The frontmatter form is singular (`dinner`, `side`, `dessert`); the
folder form is plural (`dinner/`, `sides/`, `desserts/`). Cards
without a `meal-type:` value live in `basics/` (sauces, doughs,
components).

**Required vs optional**: `aliases`, `tags`, `meal-type` (or
basics-folder placement), `cooking-time-minutes`, and `url` are
required for non-basics cards. `description`, `difficulty`, `cuisine`,
`dietary`, `servings`, `rating`, `last-cooked` are optional but
recommended — Dataview queries depend on `cuisine` and `dietary`.

## Patterns That Work

- **Mise-en-place ingredient order.** List ingredients in the order
  they're first used in preparation. The cook reads top-to-bottom;
  ordering by first use matches the cooking flow. Backed by the test
  kitchens this vault cites (NYT Cooking, Serious Eats, ATK).

- **Imperative-voice steps.** "Heat the oven" not "the oven is
  heated." Imperative is unambiguous; every food publication uses it.

- **Sub-grouped ingredients for multi-component dishes.** Use `FOR
  THE CRUST:` or `For the Sauce` headings inside `## Ingredients`
  when the recipe has 2+ components (vinaigrette + salad, dough +
  filling, sauce + base). Keeps shopping and scaling unambiguous.

- **One alias = one card.** Aliases drive Obsidian's link
  resolution. Two cards sharing an alias break wikilinks silently.

- **Wikilinks to basics.** When a step says "use [[basic-pesto-
  sauce|pesto]]", the link makes the dependency explicit and renders
  inline in Obsidian.

- **`description:` is the one-line summary.** It feeds card-level
  previews. A good description names the dish and one distinguishing
  feature ("A skillet pasta bake with cheddar and spiced caramelized
  onions"). Never a body fragment.

- **Cite well-known sources.** Test kitchens and named authors save
  the reader the cost of vetting. Per AGENTS.md: NYT Cooking, Serious
  Eats, ATK, Bon Appétit, named cookbooks. Tag `needs-review` if the
  source is weaker.

- **Singular `meal-type`, plural folder.** This vault's
  `transform_recipes.py:FOLDERS` map encodes the convention:
  `dinner→dinner/`, `side→sides/`, `dessert→desserts/`,
  `appetizer→appetizers/`. Use the singular form in frontmatter.

## Anti-Patterns

- **`description:` as a body fragment.** Setting `description: "> Description"`,
  `description: "- 4 ounces cream cheese..."`, or `description: "FOR
  THE CRUST AND TOPPING:"` happens when an importer scrapes the first
  body line. Failure: card previews display ingredient noise, not the
  dish — the most visible Dataview field is wrong.

- **Inventing ingredients.** Adding a substitution, omitting a salt
  step, or guessing a quantity because the source was unclear.
  Failure: the card no longer matches the source it cites — it's a
  different recipe wearing the citation. Per AGENTS.md, flag
  ambiguity instead of filling.

- **Curly apostrophes in filenames.** `'`, `'`, `"`, `"` in the
  filename stem cause cross-tool friction (shell quoting, URL
  encoding, git case sensitivity). Strip them; ASCII only. Display
  name keeps ASCII `'`.

- **Folder/meal-type mismatch.** A `meal-type: dinner` card filed
  under `lunch/`. Failure: the `_index.md` Dataview query
  `FROM "dinner"` misses the card.

- **Missing source citation.** No `url:` and no named cookbook
  reference. Failure: the card cannot be re-verified, and AGENTS.md's
  "well-cited sources" rule is violated.

- **Steps that reference ingredients not in the list.** Step 3
  mentions "miso paste" but it's not in the ingredients block.
  Failure: shopping list is wrong; cook is mid-recipe before
  discovering the gap.

- **AI-generated content as primary source.** Per AGENTS.md, avoid
  uncredited blog content and AI-generated recipes. They lack the
  test-kitchen vetting that makes a card trustworthy.

- **Plural `meal-type` value.** Writing `meal-type: dinners` breaks
  the FOLDERS map and the Dataview field comparisons. Always
  singular.

## Safety & Maintenance

- **Don't invent.** If the source is ambiguous (URL fetch dropped a
  step, image was unreadable on one ingredient), insert a `TODO:`
  marker at the ambiguous spot and add the `needs-review` tag. Don't
  fill the gap.

- **Cite the source.** `url:` for online sources; for cookbooks,
  put the citation as a comment line at the top of the body or in
  the alias context.

- **Re-audit on schedule.** The Tier-1 audit script
  (`check-recipe-card/scripts/audit_recipe_card.py`) catches
  structural drift (broken descriptions, mismatched folders) before
  it accumulates.

- **Repair propose-then-apply for judgment findings.** Tier-2/3
  findings are LLM judgment — the repair playbook produces a diff,
  not an auto-write. The user reviews before applying.

- **Trust the script for deterministic findings.** Tier-1 fixes
  (folder moves, filename stripping, frontmatter completion) are
  safe to auto-apply because the rules are mechanical and the
  failure modes are loud.
