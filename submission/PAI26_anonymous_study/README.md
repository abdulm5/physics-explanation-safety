# PEDB PAI26 Submission Package (Locked 60-sample)

This folder is the **only** package intended for submission.

## Included
- `paper/pai26_submission.pdf` (NeurIPS format, no appendix, 4 pages total)
- `paper/pai26_submission.tex`
- `paper/neurips_2025.sty`
- `paper/references.bib`
- `tables/*.csv` (final numeric outputs used by the manuscript)
- `figures/*.svg` (graph assets)
- `data/pedb_sources.csv` (source and licensing metadata)

## Rebuild Command
From `paper/`:

```bash
pdflatex -interaction=nonstopmode pai26_submission.tex
bibtex pai26_submission
pdflatex -interaction=nonstopmode pai26_submission.tex
pdflatex -interaction=nonstopmode pai26_submission.tex
```

## Locked Study Definition
- Prompts: 20
- Explanations: 60 (20 human, 40 AI)
- Sentence annotations used: 381 (Annotator One)
- Overlap pairs for kappa: 72
- Final taxonomy: FRAME, PRINCIPLE_DERIVE, VERIFY, INTUITION, CAVEAT

## Explicit Exclusions
Do **not** submit expanded auto-annotation drafts (90-sample exploratory branch). Only submit the files in this package.

## Headline Values in Paper
- Kappa (5-label): 0.6706
- INTUITION presence: human 35.0%, AI 20.0% (-15.0 pp)
- VERIFY presence: human 65.0%, AI 75.0% (+10.0 pp)
- Completeness means: human 5.0, AI 4.0
