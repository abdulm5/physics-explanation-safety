# PEDB Overfitting / Robustness Sanity Audit

## Scope
- Dataset: locked 60 explanations (20 human, 40 AI)
- Labels: 5-label final taxonomy
- Checks: contamination scan, prompt-level robustness, topic consistency, permutation tests, multi-comparison context, kappa uncertainty

## Contamination Check
- No `AUTO` markers found in locked annotation notes/labels/annotator fields.
- Analysis uses only `Annotator One` for full-coverage labels/ratings and `Annotator Two` only for overlap reliability pairs.

## Key Effect Robustness
- INTUITION effect (AI-human): -0.150
- Leave-one-prompt-out range: [-0.211, -0.105]
- Prompt-bootstrap 95% CI: [-0.400, +0.100]
- Permutation p-value: 0.3424

- Completeness effect (AI-human): -1.000
- Leave-one-prompt-out range: [-1.000, -1.000]
- Prompt-bootstrap 95% CI: [-1.000, -1.000]
- Permutation p-value: 0.0000

## Topic Consistency
- Electricity & Magnetism: INTUITION diff=-0.250, completeness diff=-1.000 (n_h=8, n_ai=16)
- Energy / Work / Thermo: INTUITION diff=-0.250, completeness diff=-1.000 (n_h=4, n_ai=8)
- Mechanics: INTUITION diff=+0.000, completeness diff=-1.000 (n_h=8, n_ai=16)

## Multiple-Comparison Context (5 move labels)
- FRAME: diff=+0.000, p=1.0000, BH-q=1.0000, counts(h=20/20, ai=40/40)
- PRINCIPLE_DERIVE: diff=+0.000, p=1.0000, BH-q=1.0000, counts(h=20/20, ai=40/40)
- VERIFY: diff=+0.100, p=0.4178, BH-q=1.0000, counts(h=13/20, ai=30/40)
- INTUITION: diff=-0.150, p=0.2059, BH-q=1.0000, counts(h=7/20, ai=8/40)
- CAVEAT: diff=+0.000, p=1.0000, BH-q=1.0000, counts(h=8/20, ai=16/40)

## Reliability Stability
- Observed 5-label kappa: 0.6706
- Bootstrap 95% CI for kappa: [0.4857, 0.8269]

## Verdict
- No evidence of data contamination or auto-label leakage in locked analysis files.
- Some claims are robust directionally (especially completeness), while INTUITION remains suggestive and should stay hedged.
- No catastrophic single-prompt overfitting pattern detected in leave-one-prompt-out ranges.
- Recommended language: keep INTUITION as directional pilot finding, not definitive population claim.

- Robustness flags met: completeness_effect_statistically_robust, intuition_direction_stable_lopo
