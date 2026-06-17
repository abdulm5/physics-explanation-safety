# PEDB Annotation Codebook (v2.0 Final)

## Purpose
This codebook defines the final reliability-stable discourse taxonomy used in PEDB paper analyses.

## Annotation Unit
- Primary unit: sentence-level label assignment within each explanation.
- Allowed final labels (exactly one per sentence):
  - `FRAME`
  - `PRINCIPLE_DERIVE`
  - `VERIFY`
  - `INTUITION`
  - `CAVEAT`

## Label Definitions

### `FRAME`
Function: Orients the learner to the problem setup or conceptual framing before/around reasoning.
- Positive: "Even though speed is constant, direction changes, so motion is still changing."
- Boundary: Prompt restatement with no conceptual setup.
- Non-example: Pure inferential or formula-application step.

### `PRINCIPLE_DERIVE`
Function: Invokes governing physics principle and/or advances inferential reasoning from premises to conclusion.
- Positive: "By Newton's second law, a net inward force implies centripetal acceleration."
- Boundary: Brief law mention embedded in a mostly different function sentence.
- Non-example: Standalone analogy or caveat with no reasoning advancement.

### `VERIFY`
Function: Performs an explicit check (sanity check, limiting case, unit/result consistency check).
- Positive: "In vacuum, hammer and feather fall together, matching the derived mass cancellation."
- Boundary: Vague confidence language without an actual check.
- Non-example: Assumption statement only.

### `INTUITION`
Function: Uses an analogy, everyday example, or intuitive bridge to explain concept.
- Positive: "Electric potential is like height; larger drop means more energy release."
- Boundary: Example mention that does not actually map to the concept.
- Non-example: Formal derivation without intuitive bridge.

### `CAVEAT`
Function: Marks assumptions, validity conditions, scope limits, or misconception caveats.
- Positive: "This holds for fixed voltage and negligible internal resistance."
- Boundary: Suggestive wording without explicit condition.
- Non-example: Explicit check of correctness (that is `VERIFY`).

## Tie-Break Rules (Final)
1. `PRINCIPLE_DERIVE` vs `INTUITION`
- Use `INTUITION` only when analogy/example is the primary explanatory function.
- Otherwise use `PRINCIPLE_DERIVE`.

2. `FRAME` vs `PRINCIPLE_DERIVE`
- Use `FRAME` for setup/orientation.
- Use `PRINCIPLE_DERIVE` for core scientific reasoning content.

3. `VERIFY` vs `CAVEAT`
- Use `VERIFY` only for explicit checks.
- Use `CAVEAT` for assumptions/scope limits without an explicit check.

## Reliability Notes
- Initial 6-label calibration kappa: **0.5045**.
- Dominant confusion: `PRINCIPLE` vs `DERIVE`.
- Final merged taxonomy kappa: **0.6706**.

## Rating Rubric Used in Final Paper (1-5)

### `correctness`
- 1: major scientific errors
- 3: mostly correct with notable issue
- 5: scientifically correct for intro level

### `clarity`
- 1: hard to follow
- 3: generally understandable
- 5: clear, coherent, beginner-friendly

### `completeness`
- 1: bare answer
- 3: core idea present but key steps missing
- 5: full reasoning chain

## Annotation QA Rules
- Keep sentence labels mutually exclusive.
- Log unresolved uncertainty in `notes`.
- Do not introduce new labels after freeze.
