# PEDB Project Brief (Final)

## Final Title
**Physics Explanation Discourse Bank (PEDB): A Linguistically Annotated Benchmark for Evaluating AI-Generated Physics Explanations**

## One-Sentence Pitch
PEDB evaluates whether AI-generated introductory physics explanations are not only correct, but also discourse-structured and pedagogically complete.

## Core Claim (Frozen)
Physics explanation quality is not equivalent to final-answer correctness; explanation discourse adds independent educational value.

## Final Scope (Submission)
- 20 intro-physics prompts
- 60 explanations total (20 human, 40 AI)
- Final discourse taxonomy for analysis: **5 labels**
  - `FRAME`, `PRINCIPLE_DERIVE`, `VERIFY`, `INTUITION`, `CAVEAT`
- Final holistic ratings used in paper: **3 metrics**
  - `correctness`, `clarity`, `completeness`
- Primary track: **Datasets and Benchmarks**
- Secondary relevance: **Education and Training**

## Research Questions
1. Can discourse-aware annotation provide reliable evaluation signals for physics explanations?
2. How do AI explanations differ from human explanations in discourse-move usage?
3. Which quality dimensions remain informative when correctness is near ceiling?

## Hypotheses
1. Reliability improves when high-confusion categories are merged (`PRINCIPLE` + `DERIVE`).
2. AI explanations underuse intuition-bridging discourse relative to human explanations.
3. Completeness distinguishes quality more than correctness in this pilot.

## Final Quantitative Claims (Locked)
1. Final submission reliability (5-label) is **kappa 0.6706**.
2. AI underuses `INTUITION` at explanation level (**20% vs 35%**, -15 pp).
3. AI scores lower on completeness (**4.0 vs 5.0**).

## Deliverables (Owner)
- `docs/project-brief.md`
- `docs/codebook.md`
- `docs/annotation-spec.md`
- `docs/error-taxonomy.md`
- `paper/pai26_draft.md`
- `paper/pai26_final_results.md`
- `paper/pai26_qa_pass.md`

## Current Status
- Steps 1-6: completed.
- Step 7: packaging completed in `/Users/abdulmohammad/Projects/Physics&Ling/submission/PAI26_PEDB_60` (pending only OpenReview upload + final author metadata entry).
