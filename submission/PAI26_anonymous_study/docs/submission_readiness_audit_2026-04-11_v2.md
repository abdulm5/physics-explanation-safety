# PEDB Submission Readiness Audit (2026-04-11, v2)

## Verdict
Submission package is now **ready for upload**, pending only manual OpenReview actions and final author metadata confirmation.

## Completed Since Prior Audit
1. New official NeurIPS-format PDF built from locked 60-sample numbers:
- `/Users/abdulmohammad/Projects/Physics&Ling/submission/PAI26_PEDB_60/paper/pai26_submission.pdf`
- Page count: 4 (no appendix).

2. Locked reproducibility bundle generated from the fixed workbook:
- `/Users/abdulmohammad/Projects/Physics&Ling/outputs/submission_60/*`
- Includes extracted canonical tables used for paper claims.

3. Graph assets created and packaged:
- `/Users/abdulmohammad/Projects/Physics&Ling/submission/PAI26_PEDB_60/figures/figure_move_presence_60.svg`
- `/Users/abdulmohammad/Projects/Physics&Ling/submission/PAI26_PEDB_60/figures/figure_ratings_60.svg`
- `/Users/abdulmohammad/Projects/Physics&Ling/submission/PAI26_PEDB_60/figures/figure_uncertainty_60.svg`

4. Source-attribution notes updated for legacy prompt rows in:
- `/Users/abdulmohammad/Projects/Physics&Ling/data/templates/pedb_sources.csv`

5. Submission-scope lock added:
- `/Users/abdulmohammad/Projects/Physics&Ling/submission/PAI26_PEDB_60/README.md`
- `/Users/abdulmohammad/Projects/Physics&Ling/paper/SUBMISSION_SCOPE.md`

## Current Remaining Manual Items
1. Confirm final author list in OpenReview metadata.
2. Upload the final package artifacts to OpenReview.
3. Submit before deadline.

## Locked Claim Check (60-sample package)
- Kappa (5-label): 0.6706
- INTUITION presence gap: -15.0 pp (human 35.0%, AI 20.0%)
- VERIFY presence gap: +10.0 pp (human 65.0%, AI 75.0%)
- Completeness means: human 5.0, AI 4.0

These values match the package tables in `submission/PAI26_PEDB_60/tables/`.
