# Epistemic Safety in AI Physics Tutors

This repository contains the code, data artifacts, paper files, and poster materials for **Epistemic Safety in AI Physics Tutors: Evaluating Pedagogical Structure in Generated Explanations**, a pilot study on evaluating pedagogical structure and epistemic safety in AI-generated introductory physics explanations.

The project was accepted as a poster at the **Conference on Physics and AI at Stanford University (PAI 2026)**. The official Stanford poster-session listing includes the project in Session 2 under its submitted listing title:

> A Pilot Study of Discourse Structure in AI-Generated Introductory Physics Explanations — Abdul Mohammad

Conference listing: https://datascience.stanford.edu/pai26-poster-sessions#session2

## Project Summary

The study asks whether AI physics explanations are useful for learning, not just whether they are correct. It evaluates explanations using sentence-level pedagogical discourse labels:

- `FRAME`: sets up the physical situation
- `PRINCIPLE`: states or applies a physics rule
- `VERIFY`: checks a conclusion
- `INTUITION`: gives an analogy or everyday example
- `CAVEAT`: marks assumptions or limits

The core finding is that AI explanations can match human explanations on correctness while showing lower intuition-bridging coverage and lower completeness ratings. The paper frames this as a narrow epistemic-safety issue for AI tutoring: fluent explanations can invite learner trust while hiding missing reasoning steps.

## Key Results

- Dataset: 20 introductory physics prompts, 60 explanations
- Sources: 20 human-written explanations, 40 AI-generated explanations
- Inter-annotator reliability: Cohen's kappa = 0.6706 on 72 overlap sentence pairs
- Intuition-bridging coverage: human 35% vs AI 20%
- Correctness rating: human 5.0 vs AI 5.0
- Completeness rating: human 5.0 vs AI 4.0
- Heuristic sentence-label baseline: 70.6% accuracy, 0.575 macro-F1

## Repository Layout

- `analysis/`: scripts for analysis, verification, poster generation, and robustness checks
- `data/`: prompt, source, explanation, annotation, and rating files
- `docs/`: project brief, annotation codebook, schema, and error taxonomy
- `outputs/`: generated analysis summaries, figures, tables, previews, and integrity reports
- `paper/`: paper drafts and submission-related source files
- `submission/`: final paper, poster, tables, figures, and camera-ready materials

## Main Artifacts

- Camera-ready paper: `submission/PAI26_safety_variant/paper/main.pdf`
- Paper source: `submission/PAI26_safety_variant/paper/main.tex`
- Poster PowerPoint: `submission/PAI26_safety_variant/poster/PAI26_safety_poster.pptx`
- Poster-ready figures: `outputs/paper_figures_for_poster/`
- Locked 60-sample analysis outputs: `outputs/submission_60/`

## Reproducibility

The main analysis and verification scripts are in `analysis/`. The locked 60-sample results used in the paper are under `outputs/submission_60/`.

To recompute the submission integrity checks:

```bash
python3 analysis/verify_submission60.py
python3 analysis/overfitting_sanity_audit.py
python3 analysis/heuristic_baseline.py
```

The poster-generation script uses `python-pptx`:

```bash
python3 analysis/build_pai26_safety_poster.py
```

## Citation

If citing this project, use:

```text
Mohammad, Abdul. "Epistemic Safety in AI Physics Tutors: Evaluating Pedagogical Structure in Generated Explanations." Conference on Physics and AI at Stanford University (PAI 2026), Poster Session 2.
```

The Stanford session page lists the poster under the submitted listing title, "A Pilot Study of Discourse Structure in AI-Generated Introductory Physics Explanations."
