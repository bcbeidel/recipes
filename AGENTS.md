# AGENTS.md

<!-- wiki:begin -->
Before filing new recipes or loading context beyond a skill's eager `references:`, consult `RESOLVER.md`.
<!-- wiki:end -->

## Working Agreements

- **Codify repetition.** If something will happen again, do it manually
  once on 3–10 items and show the output. If I approve, codify into a
  skill, hook, or cron. The test: if I have to ask twice, you failed.
- **Watch for patterns.** When you notice recurring work across
  sessions, propose codifying it proactively — don't wait to be asked.
- **Don't invent ingredients.** Never add, substitute, or omit
  ingredients in a recipe based on guesswork. If a source is ambiguous
  or incomplete, flag it rather than filling the gap.
- **Bias to well-cited sources.** When sourcing recipes or cooking
  advice, prefer established cookbooks, test kitchens (NYT Cooking,
  Serious Eats, ATK, Bon Appétit), or named authors with track records.
  Cite the source. Avoid uncredited blog content and AI-generated recipes.
- **Use the recipe-card skill pair.** New recipes go through
  `/build-recipe-card`, which drafts a card from a cited source
  and validates it against the shared rubric. Auditing existing cards
  goes through `/check-recipe-card` (Tier-1 deterministic +
  opt-in Tier-2/3 judgment + opt-in repair loop).
