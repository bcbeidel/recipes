---
name: build-recipe-card
description: Use when the user wants to record a recipe from a URL, image, PDF, or pasted text into the vault. Routes the input through citation, distillation, and validation; produces a single markdown card that audits clean against check-recipe-card.
allowed-tools: Read, Write, Edit, Bash, WebFetch
references:
  - ../_shared/recipe-card-best-practices.md
---

# Build Recipe-Card

Capture an existing recipe from a cited source into this vault's
recipe-card format. The principles doc is the rubric; this file is
the workflow.

**Workflow:** 1. Route → 2. Scope Gate → 3. Elicit → 4. Draft →
5. Safety Check → 6. Review Gate → 7. Save → 8. Test (handoff)

## 1. Route

Confirm the user wants to add a *new* recipe-card. If they want to:

- *Audit* existing cards → route to `/check-recipe-card`.
- *Edit* one existing card → use Edit on the file directly.
- *Plan a meal* → consult `_index.md`; this skill does not produce
  meal plans.

## 2. Scope Gate

Refuse — and recommend the alternative — when:

1. **Source is uncited.** No URL, no cookbook reference, no named
   author. AGENTS.md forbids this. Ask for a citation.

2. **Source is AI-generated content.** Per AGENTS.md, avoid
   AI-generated recipes. Decline and ask for a credible source.

3. **Source credibility is low** (uncredited blog, untested-looking
   content). Warn with what's weak ("uncredited blogspot post"), and
   ask the user to confirm. On confirm, proceed but **tag the
   resulting card with `needs-review`** so the audit catches it.

4. **Card already exists.** Filename or alias collision in the vault
   (run a quick `Glob` over recipe folders before drafting). Offer
   to update the existing card instead.

## 3. Elicit

Accept any of these inputs:

- **URL** — fetch with WebFetch, extract title / ingredients / steps.
- **Pasted text** — parse directly from the user's message.
- **Image** (single, or composite of a multi-page recipe stitched
  externally) — read with Read.
- **PDF** — read with Read using `pages:` for cookbook scans.

Extract:

- Recipe title (becomes the alias in Title Case).
- Ingredients in order of first use.
- Numbered preparation steps in imperative voice.
- Yield/servings, total time, source URL or citation.
- Cuisine, dietary tags, difficulty (judgment).

If extraction is partial (URL fetch trimmed steps, image was unclear
on one ingredient), surface the gap explicitly — do not infer.

## 4. Draft

Build the card per the *Anatomy* section of the principles doc:

- **Filename**: kebab-case stem from the title; strip curly
  apostrophes (`'`, `'`, `"`, `"`).
- **Folder**: derived from chosen `meal-type` per the RESOLVER.md
  filing table. Singular meal-type → plural folder
  (`dinner→dinner/`, `side→sides/`, `dessert→desserts/`,
  `appetizer→appetizers/`). If unclear (a sauce that's also a meal),
  use `basics/` and tag `needs-review`.
- **`description:`**: one-sentence summary naming the dish and one
  distinguishing feature. Never a body fragment.
- **Frontmatter**: every required field per the principles doc
  *Anatomy*.
- **Body**: `## Ingredients` (bullets, sub-grouped if
  multi-component) → `---` → `## Preparation` (numbered, imperative
  voice).

## 5. Safety Check

Apply the *Anti-Patterns* from the principles doc as a pre-write
checklist:

- No invented ingredients — every bullet appears in the source.
- No omitted ingredients from the source.
- Quantities match the source verbatim.
- Curly apostrophes stripped from filename.
- Folder matches `meal-type` (singular→plural mapping).
- `description:` is a real summary, not a body fragment.
- Source is cited (`url:` or in-body cookbook reference).

If the source is ambiguous on any single point, insert a `TODO:
source ambiguity at <step>` marker and tag the card `needs-review`.
**Do not fill from guesswork.**

## 6. Review Gate

Present the drafted card to the user with:

- Filename and target folder.
- The full frontmatter block.
- Body preview (first 5 ingredients, first 3 steps).
- Any `TODO:` markers or applied `needs-review` tag.
- Credibility note if the source was flagged in Step 2.

Wait for explicit approval. Revise on request.

## 7. Save

Write the file to `<folder>/<kebab-case-name>.md`. Use Write — the
file is new. Do not modify `_index.md` (it's Dataview-driven and
auto-populates).

## 8. Test (handoff)

Run the Tier-1 audit script on the new file:

```bash
python3 .claude/skills/check-recipe-card/scripts/audit_recipe_card.py \
  <folder>/<filename>.md
```

It should exit 0. If it exits 1, route the findings to
`/check-recipe-card` for repair.

## Anti-Pattern Guards

1. **Inventing to fill gaps.** AGENTS.md rule. If the source is
   unclear, mark `TODO:` and tag `needs-review`. Never guess.
2. **Skipping the Review Gate.** A card written without preview is
   a card written without verification — Anti-Pattern from the
   principles doc.
3. **Filing by guess.** If `meal-type` is unclear, use `basics/`
   and let the user move it. Do not invent a meal-type value.
4. **Auto-tagging credibility silently.** If the source warranted a
   `needs-review` tag, name that explicitly at the Review Gate so
   the user can override.

## Handoff

**Receives:** URL, pasted text, image, or PDF; user citation
context.

**Produces:** One markdown file under the appropriate folder, audits
clean under Tier-1.

**Chainable to:** `/check-recipe-card` (single-file mode) for
end-to-end validation; `/check-recipe-card --folder <folder>`
to confirm the new card hasn't broken any cross-vault constraint
(alias / filename uniqueness).
