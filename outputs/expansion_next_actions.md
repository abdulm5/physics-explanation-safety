# PEDB Expansion: Next Actions (After Auto Steps)

## Completed by assistant
- Expanded to 30 prompts and 90 explanations.
- Added 10 sourced human explanations (P21-P30).
- Generated 20 AI explanations (ChatGPT + Sonnet) for P21-P30.
- Built 24-row overlap selection for Annotator 2.
- Ran structural QA (3 rows per prompt, 30/60 source balance).

## Your immediate tasks
1. Import `data/processed/pedb_explanations_append_30.csv` into your spreadsheet `explanations` tab.
2. Annotate the new 30 explanations (sentence labels + ratings) with final 5-label codebook.
3. Give `data/annotations/pedb_overlap_selection_24.csv` to Annotator 2 for blind second pass.
4. Resolve disagreements and finalize `label_final` on overlap rows.

## Then send back
- Updated spreadsheet export with new annotations and ratings.

## I will then run
- Updated kappa on expanded overlap.
- Recomputed prevalence/rating/correlation tables.
- Recomputed uncertainty CIs/p-values.
- Final manuscript number refresh.
