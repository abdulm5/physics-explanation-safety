# PEDB Submission Readiness Audit (2026-04-11)

## Verdict
Not 100% submittable yet.

The core 60-explanation results are internally consistent and reproducible from the locked workbook, but the actual submission artifact set is not fully aligned.

## What Passed
1. **Conference policy match**
- PAI26 requires NeurIPS format, 4 pages max excluding references, no appendix, OpenReview submission, and double-blind except datasets track single-blind.
- Source: Stanford CFP lines 157-164.

2. **Final 60-sample quantitative claims verify from workbook**
- Workbook has 20 prompts, 60 explanations (20 human, 40 AI), 381 annotator-one sentence labels, and 72 overlap pairs.
- Recomputed 5-label kappa from overlap pairs: 0.6706 (Po=0.8333).
- Recomputed move prevalence and rating means match locked 60-sample claims:
  - INTUITION presence gap: -15 pp (human 35%, AI 20%).
  - VERIFY presence gap: +10 pp (human 65%, AI 75%).
  - Completeness mean gap: -1.0 (human 5.0, AI 4.0).

3. **No unresolved review queue in locked 60 analysis**
- `outputs/analysis_summary_step6_final.md` reports `REVIEW` rows remaining: 0.

## Blocking Issues (Must Fix Before Submission)
1. **Submission PDF is outdated relative to locked results**
- Only PDF found: `/Users/abdulmohammad/Downloads/PEDB_Paper.pdf`.
- That PDF describes an older design (15-item pilot subset, 6-label taxonomy) and does not reflect the current locked 60-item/5-label results.
- It also carries a NeurIPS 2025 footer string and old checklist text.

2. **No final submission artifact in project workspace**
- No `.tex` or final `.pdf` in `/Users/abdulmohammad/Projects/Physics&Ling`.
- Current manuscript is markdown only: `/Users/abdulmohammad/Projects/Physics&Ling/paper/pai26_draft.md`.

3. **Conflicting analysis branches are both present**
- 60-sample locked story:
  - `/Users/abdulmohammad/Projects/Physics&Ling/paper/pai26_final_results.md`
- 90-sample expanded story with contradictory INTUITION direction and explicit draft warning:
  - `/Users/abdulmohammad/Projects/Physics&Ling/paper/pai26_final_results_expanded_auto.md`
- If both are exposed in supplementary materials, reviewers can flag inconsistency.

4. **Source-provenance notes still marked unresolved for legacy prompts**
- `/Users/abdulmohammad/Projects/Physics&Ling/data/templates/pedb_sources.csv` rows for M01-T04 still say: "verify attribution before public release."

5. **Historical 6-label kappa (0.5045) is not reproducible from current canonical files alone**
- Current canonical sentence labels are already merged to `PRINCIPLE_DERIVE`.
- If you keep the 0.5045 claim, provide a provenance note or archived pre-merge calibration table in supplementary.

## Non-Blocking Risks (Report Transparently)
1. **Completeness difference is deterministic in current table**
- Within-group SD is 0.0 for completeness in 60-sample summary.
- Keep interpretation cautious and avoid overclaiming inferential strength.

2. **Single full-coverage rater stream for aggregate ratings**
- This is acceptable for pilot framing but must remain explicit as a limitation.

## Minimum Actions to Reach "Submittable"
1. Build and lock a new final PDF from the current 60-sample manuscript (NeurIPS format, 4-page body + references).
2. Use only one narrative branch in the submission package:
- Either lock to 60-sample results and archive expanded files out of submission scope, or fully re-annotate and switch everything to 90-sample consistently.
3. Resolve legacy source-attribution notes in `pedb_sources.csv`.
4. Add one short reproducibility note for the 0.5045 pre-merge kappa claim (or remove that claim from the final draft).
5. Complete OpenReview metadata and track settings per CFP.

## Suggested Submission Lock
For fastest safe submission:
1. Lock to the 60-sample branch.
2. Exclude expanded-auto files from supplementary.
3. Submit final PDF + final tables + one concise reproducibility/readme note.
