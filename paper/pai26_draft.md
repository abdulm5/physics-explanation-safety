# PEDB-Pilot: A Discourse Benchmark for Evaluating AI-Generated Physics Explanations

## Abstract
Large language models can generate fluent introductory physics explanations, but fluency alone does not guarantee pedagogical quality. We present PEDB-Pilot, a benchmark of 60 explanations (20 human, 40 AI) across 20 conceptual prompts in mechanics, electricity and magnetism, and thermo/energy topics. We annotate explanations with a discourse taxonomy and holistic quality ratings. A calibration subset of 12 explanations (72 paired sentence labels) yielded moderate reliability in an initial 6-label scheme (Cohen's kappa = 0.5045), with dominant confusion between PRINCIPLE and DERIVE. After a reliability-driven taxonomy refinement merging those two into PRINCIPLE_DERIVE, reliability improved to kappa = 0.6706 without adjudication-based relabeling. Final 5-label analyses show AI explanations underuse INTUITION moves at the explanation level (20% vs 35% for human, -15 pp) and score lower on completeness (4.0 vs 5.0).

## 1. Introduction
AI-generated educational explanations are increasingly common in physics learning workflows. Current evaluation practices often focus on answer correctness, readability, or broad preference judgments, while underemphasizing explanation structure. In physics pedagogy, however, effective explanations require discourse moves such as contextual framing, explicit reasoning progression, assumption handling, and intuitive bridges.

PEDB-Pilot evaluates explanation quality as a discourse-structural property. The benchmark pairs human and AI responses to the same prompts and supports sentence-level move analysis plus holistic ratings. The objective is not only to test whether an explanation is correct, but whether it is instructionally useful.

Contributions:
1. A paired corpus of 60 introductory-physics explanations over 20 prompts.
2. A reliability-tested discourse taxonomy for explanation analysis.
3. Quantitative comparisons of move usage and quality ratings across human and AI explanations.
4. A transparent reliability refinement path from a 6-label to a 5-label scheme.

Core claims tested in this paper:
1. Taxonomy reliability is materially improved by merging the dominant confusion pair (PRINCIPLE and DERIVE), raising kappa from 0.5045 to 0.6706.
2. Relative to human explanations, AI explanations in this pilot underuse intuition-bridging discourse (20% vs 35% explanation-level presence).
3. In this dataset, correctness is near ceiling for both sources, while completeness better separates quality (AI 4.0 vs human 5.0).

## 2. Related Work
Physics reasoning benchmarks have advanced answer-level and derivation-level evaluation, but less often evaluate explanation discourse quality. In parallel, NLP work on educational and explanatory text has shown that didactic structure can be annotated and measured. PEDB-Pilot integrates these directions by introducing a discourse-aware physics explanation benchmark.

## 3. Dataset and Annotation
### 3.1 Dataset scope
PEDB-Pilot contains:
- 20 prompts: 8 mechanics, 8 electricity and magnetism, 4 thermo/energy.
- 60 explanations total: 20 human and 40 AI (2 AI responses per prompt).

### 3.2 Annotation protocol
Each explanation is segmented into sentences and labeled at sentence level by discourse move.

Initial calibration used a 6-label taxonomy:
- FRAME
- PRINCIPLE
- DERIVE
- VERIFY
- INTUITION
- CAVEAT

Holistic ratings (1-5):
- clarity
- correctness
- completeness

### 3.3 Reliability and taxonomy refinement
Calibration subset: 12 explanations, 72 paired sentence labels.

Initial reliability (6 labels):
- Cohen's kappa: 0.5045
- Observed agreement (Po): 0.6389

Dominant disagreement pair:
- PRINCIPLE -> DERIVE (10 cases)

Given systematic overlap between law invocation and inferential step labels, we refined the taxonomy by merging PRINCIPLE and DERIVE into PRINCIPLE_DERIVE.

Refined reliability (5 labels):
- Labels: FRAME, PRINCIPLE_DERIVE, VERIFY, INTUITION, CAVEAT
- Cohen's kappa: 0.6706
- Observed agreement (Po): 0.8333

All final analyses below use this 5-label taxonomy.

This refinement was chosen from observed confusion patterns in the calibration set and applied uniformly to final analyses; it was not produced by post-hoc consensus relabeling.

## 4. Experimental Setup
We compare human vs AI explanations on:
1. Sentence-level move distribution.
2. Explanation-level move presence rates.
3. Holistic rating summaries.
4. Move-rating correlations (Pearson r).
5. Uncertainty estimates for key contrasts (95% CIs; two-proportion tests for move-presence differences).

For ratings, we use one consistent rater stream (`Annotator_1`) across all 60 explanations to avoid mixed-rater sparsity artifacts.

## 5. Results
### 5.1 Move prevalence (human vs AI)
Explanation-level presence rates:
- FRAME: human 100%, AI 100% (0 pp)
- PRINCIPLE_DERIVE: human 100%, AI 100% (0 pp)
- VERIFY: human 65%, AI 75% (+10 pp AI)
- INTUITION: human 35%, AI 20% (-15 pp AI)
- CAVEAT: human 40%, AI 40% (0 pp)

Sentence-level distribution:
- Human (n=121 sentences): FRAME 16.53%, PRINCIPLE_DERIVE 55.37%, VERIFY 13.22%, INTUITION 6.61%, CAVEAT 8.26%
- AI (n=260 sentences): FRAME 15.38%, PRINCIPLE_DERIVE 54.62%, VERIFY 15.38%, INTUITION 3.85%, CAVEAT 10.77%

Main structural gap is lower AI use of INTUITION moves.

### 5.2 Holistic ratings
Source-level means (Annotator_1):
- Human (n=20): clarity 5.0, correctness 5.0, completeness 5.0
- AI (n=40): clarity 4.875, correctness 5.0, completeness 4.0

Largest rating difference is completeness (-1.0 for AI vs human).

### 5.3 Move-rating correlations
Across 60 explanations:
- VERIFY vs clarity: r = 0.2119
- CAVEAT vs clarity: r = 0.2462
- INTUITION vs completeness: r = 0.1633
- VERIFY vs completeness: r = -0.1046

Correlation magnitudes are small and should be interpreted as exploratory in this pilot.

### 5.4 Uncertainty estimates (current dataset)
Inference from current aggregate outputs indicates:
- INTUITION presence difference (AI - human): -15.0 pp (95% CI -39.3 to 9.3 pp), p=0.206.
- VERIFY presence difference (AI - human): +10.0 pp (95% CI -14.8 to 34.8 pp), p=0.418.
- Clarity mean difference (AI - human): -0.125 (95% CI -0.228 to -0.022), p=0.017.
- Completeness mean difference (AI - human): -1.000 (95% CI -1.000 to -1.000) in the present table, reflecting zero within-group variance in recorded completeness scores.

These intervals suggest directional effects for discourse gaps, but with uncertainty still large for move-presence contrasts at this sample size.

## 6. Discussion
Two results are central. First, taxonomy reliability depends heavily on category separability: the PRINCIPLE/DERIVE split produced moderate agreement, while the merged PRINCIPLE_DERIVE category produced substantial agreement suitable for pilot benchmarking. Second, AI explanations in this dataset are frequently fluent and formally correct, but comparatively weaker on intuitive bridging and completeness.

This supports discourse-aware evaluation as a complement to answer-level metrics for educational AI.

## 7. Limitations
- Pilot scale (60 explanations) limits generalization.
- One-rater dominance in final full-coverage rating pass introduces potential scorer bias.
- Ceiling effects in ratings (especially correctness) reduce variance for correlation analysis.
- Sentence segmentation is rule-based and may blur clause-level distinctions.
- Significance estimates are preliminary and based on current aggregate outputs; final inference should be rerun after dataset expansion.
- Current uncertainty estimates are based on aggregate outputs; final inferential reporting should be rerun on expanded raw data.

## 8. Conclusion
PEDB-Pilot provides a compact, reliability-audited benchmark for discourse-sensitive evaluation of AI-generated physics explanations. The benchmark shows that structure-level analysis can surface differences not captured by correctness alone and offers a practical template for larger physics explanation evaluation resources.

## References
- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37-46.
- Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159-174.
- Artstein, R., & Poesio, M. (2008). Inter-coder agreement for computational linguistics. *Computational Linguistics*, 34(4), 555-596.
- PhysReason: A Comprehensive Benchmark towards Physics-Based Reasoning. arXiv:2502.12054.
- UGPhysics: A Comprehensive Benchmark for Undergraduate Physics Reasoning with Large Language Models. arXiv:2502.00334.
- 2026 Conference on Physics and AI (PAI26) CFP. Stanford Data Science. [https://datascience.stanford.edu/events/center-decoding-universe/c4du-annual-conference/2026-conference-physics-and-ai-pai26](https://datascience.stanford.edu/events/center-decoding-universe/c4du-annual-conference/2026-conference-physics-and-ai-pai26)
