import csv
import math
from pathlib import Path

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
MOVE_CSV = BASE / 'outputs' / 'table_move_prevalence_final.csv'
RATING_CSV = BASE / 'outputs' / 'table_ratings_summary_final.csv'
OUT_CSV = BASE / 'outputs' / 'table_uncertainty_estimates_final.csv'
OUT_MD = BASE / 'outputs' / 'uncertainty_summary_final.md'

# Fixed from dataset design
N_HUMAN = 20
N_AI = 40
Z95 = 1.959963984540054


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def two_prop_wald_ci(x1: int, n1: int, x2: int, n2: int):
    # difference = p2 - p1
    p1 = x1 / n1
    p2 = x2 / n2
    diff = p2 - p1
    se = math.sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
    lo = diff - Z95 * se
    hi = diff + Z95 * se
    return diff, se, lo, hi


def two_prop_ztest_pvalue(x1: int, n1: int, x2: int, n2: int):
    p1 = x1 / n1
    p2 = x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se_pool == 0:
        return 1.0, 0.0
    z = (p2 - p1) / se_pool
    p = 2 * (1 - normal_cdf(abs(z)))
    return p, z


def welch_mean_diff_ci(mean1, sd1, n1, mean2, sd2, n2):
    # difference = mean2 - mean1
    diff = mean2 - mean1
    v1 = (sd1 ** 2) / n1
    v2 = (sd2 ** 2) / n2
    se = math.sqrt(v1 + v2)
    if se == 0:
        return diff, 0.0, diff, diff, float('inf'), 1.0, 0.0

    # Welch-Satterthwaite df
    num = (v1 + v2) ** 2
    den = 0.0
    if n1 > 1 and v1 > 0:
        den += (v1 ** 2) / (n1 - 1)
    if n2 > 1 and v2 > 0:
        den += (v2 ** 2) / (n2 - 1)
    df = num / den if den > 0 else float('inf')

    # Use normal critical as robust fallback to avoid scipy dependency
    lo = diff - Z95 * se
    hi = diff + Z95 * se
    z = diff / se
    p = 2 * (1 - normal_cdf(abs(z)))
    return diff, se, lo, hi, df, p, z


move_rows = []
with MOVE_CSV.open(newline='') as f:
    for r in csv.DictReader(f):
        move_rows.append(r)

rating_rows = {}
with RATING_CSV.open(newline='') as f:
    for r in csv.DictReader(f):
        rating_rows[r['source']] = r

results = []

# Proportion inferences for all explanation-level moves
for r in move_rows:
    move = r['move']
    p_h = float(r['human_expl_presence_pct']) / 100.0
    p_a = float(r['ai_expl_presence_pct']) / 100.0
    x_h = int(round(p_h * N_HUMAN))
    x_a = int(round(p_a * N_AI))

    diff, se, lo, hi = two_prop_wald_ci(x_h, N_HUMAN, x_a, N_AI)
    pval, z = two_prop_ztest_pvalue(x_h, N_HUMAN, x_a, N_AI)

    results.append({
        'metric': f'move_presence_diff_ai_minus_human::{move}',
        'group_human_n': N_HUMAN,
        'group_ai_n': N_AI,
        'human_count': x_h,
        'ai_count': x_a,
        'estimate': diff,
        'se': se,
        'ci95_low': lo,
        'ci95_high': hi,
        'z_stat': z,
        'p_value': pval,
        'method': 'two_proportion_wald_ci + pooled_z_test'
    })

# Rating differences using available summary stats
h = rating_rows['human']
a = rating_rows['ai']

for metric in ('clarity', 'correctness', 'completeness'):
    m_h = float(h[f'{metric}_mean'])
    sd_h = float(h[f'{metric}_sd'])
    n_h = int(h['n'])

    m_a = float(a[f'{metric}_mean'])
    sd_a = float(a[f'{metric}_sd'])
    n_a = int(a['n'])

    diff, se, lo, hi, df, p, z = welch_mean_diff_ci(m_h, sd_h, n_h, m_a, sd_a, n_a)
    method = 'welch_from_summary_normal_ci'
    if se == 0:
        method = 'deterministic_from_summary_no_variance'

    results.append({
        'metric': f'rating_mean_diff_ai_minus_human::{metric}',
        'group_human_n': n_h,
        'group_ai_n': n_a,
        'human_count': '',
        'ai_count': '',
        'estimate': diff,
        'se': se,
        'ci95_low': lo,
        'ci95_high': hi,
        'z_stat': z,
        'p_value': p,
        'method': method
    })

with OUT_CSV.open('w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    w.writeheader()
    w.writerows(results)

# Build concise markdown summary for paper integration
res_by_metric = {r['metric']: r for r in results}
intu = res_by_metric['move_presence_diff_ai_minus_human::INTUITION']
verify = res_by_metric['move_presence_diff_ai_minus_human::VERIFY']
clar = res_by_metric['rating_mean_diff_ai_minus_human::clarity']
comp = res_by_metric['rating_mean_diff_ai_minus_human::completeness']

with OUT_MD.open('w') as f:
    f.write('# PEDB Uncertainty Addendum (Current Data)\n\n')
    f.write('Source tables:\n')
    f.write('- `outputs/table_move_prevalence_final.csv`\n')
    f.write('- `outputs/table_ratings_summary_final.csv`\n\n')
    f.write('## Primary contrasts\n')
    f.write(
        f"- INTUITION move presence (AI - human): {float(intu['estimate'])*100:.1f} pp "
        f"(95% CI {float(intu['ci95_low'])*100:.1f} to {float(intu['ci95_high'])*100:.1f} pp), "
        f"z={float(intu['z_stat']):.2f}, p={float(intu['p_value']):.3f}.\n"
    )
    f.write(
        f"- VERIFY move presence (AI - human): {float(verify['estimate'])*100:.1f} pp "
        f"(95% CI {float(verify['ci95_low'])*100:.1f} to {float(verify['ci95_high'])*100:.1f} pp), "
        f"z={float(verify['z_stat']):.2f}, p={float(verify['p_value']):.3f}.\n"
    )
    f.write(
        f"- Clarity mean difference (AI - human): {float(clar['estimate']):.3f} "
        f"(95% CI {float(clar['ci95_low']):.3f} to {float(clar['ci95_high']):.3f}), "
        f"z={float(clar['z_stat']):.2f}, p={float(clar['p_value']):.3f}.\n"
    )
    f.write(
        f"- Completeness mean difference (AI - human): {float(comp['estimate']):.3f} "
        f"(95% CI {float(comp['ci95_low']):.3f} to {float(comp['ci95_high']):.3f}); "
        f"both groups had zero within-group SD in summary table.\n"
    )
    f.write('\n## Notes\n')
    f.write('- Inference is computed from currently available aggregate outputs.\n')
    f.write('- After tomorrow\'s data expansion, rerun this script for final inferential reporting.\n')

print(f'Wrote: {OUT_CSV}')
print(f'Wrote: {OUT_MD}')
