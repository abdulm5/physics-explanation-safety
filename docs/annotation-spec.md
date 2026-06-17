# PEDB Annotation Specification (v2.0 Final)

## Dataset Scope
- Prompts: `20`
- Explanations: `60` (`20` human, `40` AI)
- Final analysis taxonomy: `FRAME`, `PRINCIPLE_DERIVE`, `VERIFY`, `INTUITION`, `CAVEAT`

## File 1: Sentence-Level Annotations (Canonical)
Path: `data/annotations/pedb_sentence_annotations.csv`

### Required Header
```csv
explanation_id,prompt_id,topic,source_type,sentence_id,sentence_text,label_annotator_1,label_annotator_2,label_final,adjudication_note,notes
```

### Constraints
- `label_*` values must be one of:
  - `FRAME`
  - `PRINCIPLE_DERIVE`
  - `VERIFY`
  - `INTUITION`
  - `CAVEAT`
- `sentence_id` is integer and unique within each `explanation_id`.
- `label_final` is required for all rows used in analysis.

## File 2: Explanation-Level Ratings
Path: `data/annotations/pedb_explanation_ratings.csv`

### Required Header
```csv
explanation_id,prompt_id,topic,source_type,annotator_id,correctness,clarity,completeness,notes
```

### Constraints
- `correctness`, `clarity`, `completeness` must be integers in `[1,5]`.
- Exactly one final rating row per explanation for the rater stream used in paper-level aggregates.

## Derived Table Logic (for Results)
1. Explanation-level move presence:
- For each explanation and each move, set presence=1 if **any sentence** has that `label_final`.
2. Sentence-level distribution:
- Compute percentage of sentence labels by source type.
3. Ratings summary:
- Compute mean and SD by source type.

## Backward Compatibility (Calibration)
- If using legacy 6-label calibration rows, map:
  - `PRINCIPLE` -> `PRINCIPLE_DERIVE`
  - `DERIVE` -> `PRINCIPLE_DERIVE`
- Keep original labels in archived files; use mapped labels for final analyses.

## Quality Gates
1. No missing `label_final` in analysis rows.
2. No invalid label values.
3. Rating ranges validated (`1..5`).
4. Prompt coverage: exactly 3 explanations per prompt (1 human + 2 AI).
5. `REVIEW` queue cleared before final export.

## Handoff Outputs Required
- `outputs/table_move_prevalence_final.csv`
- `outputs/table_ratings_summary_final.csv`
- `outputs/table_move_rating_correlations_final.csv`
- `outputs/analysis_summary_step6_final.md`
