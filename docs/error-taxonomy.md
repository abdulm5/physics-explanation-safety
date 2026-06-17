# PEDB Error Taxonomy (AI Explanation Failures)

This taxonomy defines recurring failure modes expected during annotation and analysis. Each type includes one representative example to support paper-ready qualitative analysis.

## E1. Formula Drop Without Interpretation
**Definition:** The response gives an equation or algebraic statement but does not explain physical meaning.

**Example:**
"Using F = ma, acceleration is F/m. Therefore acceleration increases."  
(No interpretation of force direction, net force, or physical mechanism.)

## E2. Causal Thinness
**Definition:** The response states correlation or outcome but omits mechanistic why-links.

**Example:**
"When resistance increases, current decreases."  
(Outcome stated, but no causal account of charge flow or fixed-voltage condition.)

## E3. Hidden Assumptions
**Definition:** The response relies on idealizations or boundary conditions without stating them.

**Example:**
"Pressure rises with temperature in the container."  
(No mention of fixed volume, closed system, or ideal-gas approximation.)

## E4. Misconception Non-Repair
**Definition:** The response misses an obvious learner misconception that should be corrected explicitly.

**Example:**
"The object moves at constant speed in a circle."  
(No explicit correction that constant speed can still imply nonzero acceleration.)

## E5. Step Gaps in Reasoning Chain
**Definition:** The response jumps from principle to conclusion without intermediate inferential steps.

**Example:**
"By conservation of energy, the speed at the bottom is higher."  
(Intermediate conversion logic and terms are omitted.)

## E6. Analogy Drift
**Definition:** The response uses analogy that is under-mapped, overextended, or potentially misleading.

**Example:**
"Voltage is like water pressure, so electrons are literally water flowing in a pipe."  
(Analogy is presented as identity, causing conceptual distortion.)

## E7. Fluent Overconfidence
**Definition:** Highly polished wording masks incompleteness or subtle conceptual error, creating high fluency risk.

**Example:**
"This definitively proves acceleration is zero because speed does not change."  
(Confident style contradicts correct circular-motion reasoning.)

## Usage in Results Section
- Tag each major qualitative example with one primary taxonomy code (`E1`-`E7`).
- Allow one optional secondary code when two failures are inseparable.
- Use taxonomy frequencies to support error-pattern claims.

## Mapping to Final PEDB Taxonomy (v2.0)
- `E1` -> weak/partial `PRINCIPLE_DERIVE` support and lower `completeness`
- `E2` -> weak/partial `PRINCIPLE_DERIVE` support and lower `completeness`
- `E3` -> missing or weak `CAVEAT`
- `E4` -> missing corrective qualification (typically weak `CAVEAT`, sometimes weak `FRAME`)
- `E5` -> compressed `PRINCIPLE_DERIVE` chain with lower `completeness`
- `E6` -> `INTUITION` present but paired with lower `correctness` or lower `completeness`
- `E7` -> relatively high `clarity` with lower `completeness`
