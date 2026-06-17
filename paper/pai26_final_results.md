# PEDB Final Results (PAI26 Draft-Ready)

## 1) Dataset Summary
- Source workbook for final analysis: `/Users/abdulmohammad/Downloads/PEDB_Final_Spreadsheet__7__step5_done_fixed.xlsx`
- Total explanations: 60
- Human explanations: 20
- AI explanations: 40
- Topics: mechanics, electricity and magnetism, thermo/energy
- Annotation rows used (sentence-level, Annotator One): 381
- Remaining `REVIEW` rows: 0

## 2) Reliability (Calibration Subset)
Calibration set: 12 explanations, 72 paired sentence labels.

### Initial 6-label scheme
- Labels: `FRAME`, `PRINCIPLE`, `DERIVE`, `VERIFY`, `INTUITION`, `CAVEAT`
- Cohen's kappa: **0.5045**
- Observed agreement (Po): 0.6389

### Final 5-label scheme (after taxonomy refinement)
- Labels: `FRAME`, `PRINCIPLE_DERIVE`, `VERIFY`, `INTUITION`, `CAVEAT`
- Cohen's kappa: **0.6706**
- Observed agreement (Po): 0.8333

Interpretation: reliability improved after merging the dominant confusion pair (`PRINCIPLE` vs `DERIVE`) without adjudication-based label copying.

## 3) Move Prevalence Results
Source table: `/Users/abdulmohammad/Projects/Physics&Ling/outputs/table_move_prevalence_final.csv`

### Explanation-level presence (% of explanations containing move)
- `FRAME`: human 100.0%, AI 100.0% (AI - human: 0.0 pp)
- `PRINCIPLE_DERIVE`: human 100.0%, AI 100.0% (0.0 pp)
- `VERIFY`: human 65.0%, AI 75.0% (+10.0 pp)
- `INTUITION`: human 35.0%, AI 20.0% (**-15.0 pp**)
- `CAVEAT`: human 40.0%, AI 40.0% (0.0 pp)

### Sentence-level distribution
Human sentences (n=121):
- `FRAME` 16.53%
- `PRINCIPLE_DERIVE` 55.37%
- `VERIFY` 13.22%
- `INTUITION` 6.61%
- `CAVEAT` 8.26%

AI sentences (n=260):
- `FRAME` 15.38%
- `PRINCIPLE_DERIVE` 54.62%
- `VERIFY` 15.38%
- `INTUITION` 3.85%
- `CAVEAT` 10.77%

Primary structural gap: AI explanations underuse `INTUITION` moves compared with human explanations.

## 4) Holistic Rating Results
Source table: `/Users/abdulmohammad/Projects/Physics&Ling/outputs/table_ratings_summary_final.csv`

Using one full-coverage rater stream (`Annotator_1`):
- Human (n=20): clarity 5.0, correctness 5.0, completeness 5.0
- AI (n=40): clarity 4.875, correctness 5.0, completeness 4.0

Largest difference: completeness (**-1.0**, AI minus human).

## 5) Move-Rating Correlations
Source table: `/Users/abdulmohammad/Projects/Physics&Ling/outputs/table_move_rating_correlations_final.csv`

Reported Pearson correlations:
- `VERIFY` vs clarity: 0.2119
- `VERIFY` vs completeness: -0.1046
- `INTUITION` vs clarity: 0.0348
- `INTUITION` vs completeness: 0.1633
- `CAVEAT` vs clarity: 0.2462
- `CAVEAT` vs completeness: 0.0

`FRAME` and `PRINCIPLE_DERIVE` correlations are blank because those moves are present in 100% of explanations (no variance).

## 6) Uncertainty Estimates (Current Dataset)
Source files:
- `/Users/abdulmohammad/Projects/Physics&Ling/outputs/table_uncertainty_estimates_final.csv`
- `/Users/abdulmohammad/Projects/Physics&Ling/outputs/uncertainty_summary_final.md`

Key contrasts:
- INTUITION presence (AI - human): -15.0 pp (95% CI -39.3 to 9.3 pp), p=0.206
- VERIFY presence (AI - human): +10.0 pp (95% CI -14.8 to 34.8 pp), p=0.418
- Clarity mean difference (AI - human): -0.125 (95% CI -0.228 to -0.022), p=0.017
- Completeness mean difference (AI - human): -1.000 (95% CI -1.000 to -1.000) in current summary table

Interpretation:
- Move-presence effects are directionally informative but currently imprecise.
- Clarity difference is small in magnitude despite statistical detectability.
- Completeness contrast is deterministic in current ratings table and should be re-checked after data expansion.

## 7) Claim-Ready Findings for the Paper
1. **Reliability claim:** The 5-label taxonomy is substantially more reliable than the original 6-label taxonomy (kappa 0.6706 vs 0.5045).
2. **Discourse gap claim:** AI explanations show a lower rate of intuition-bridging discourse at explanation level (20% vs 35%; -15 pp).
3. **Quality gap claim:** AI explanations are near-ceiling on correctness but lower on completeness (4.0 vs 5.0).
4. **Interpretive claim:** In this pilot, correctness alone does not distinguish outputs well; discourse structure and completeness provide the main separation signal.

## 8) Reporting Notes (for NeurIPS-style 4-page submission)
- Keep all main quantitative claims tied directly to one table/figure.
- Report the taxonomy change transparently as a reliability-driven refinement.
- Explicitly list limitations: pilot size, one-rater full-coverage ratings, and ceiling effects in correctness.
