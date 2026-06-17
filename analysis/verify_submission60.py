import csv
from pathlib import Path

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
SUB = BASE / 'submission' / 'PAI26_PEDB_60'
OUT = BASE / 'outputs' / 'submission_60' / 'final_integrity_report.md'

prev = list(csv.DictReader((SUB / 'tables' / 'table_move_prevalence_final.csv').open()))
ratings = list(csv.DictReader((SUB / 'tables' / 'table_ratings_summary_final.csv').open()))
kappa = list(csv.DictReader((SUB / 'tables' / 'table_overlap_kappa_final.csv').open()))[0]

by_move = {r['move']: r for r in prev}
by_src = {r['source']: r for r in ratings}

checks = []

def check(name, cond, got=None, expected=None):
    checks.append((name, cond, got, expected))

check('kappa_5label', abs(float(kappa['kappa']) - 0.6706) < 1e-6, kappa['kappa'], '0.6706')
check('overlap_pairs', int(kappa['n_pairs']) == 72, kappa['n_pairs'], '72')
check('intuition_human_presence', float(by_move['INTUITION']['human_expl_presence_pct']) == 35.0, by_move['INTUITION']['human_expl_presence_pct'], '35.0')
check('intuition_ai_presence', float(by_move['INTUITION']['ai_expl_presence_pct']) == 20.0, by_move['INTUITION']['ai_expl_presence_pct'], '20.0')
check('verify_human_presence', float(by_move['VERIFY']['human_expl_presence_pct']) == 65.0, by_move['VERIFY']['human_expl_presence_pct'], '65.0')
check('verify_ai_presence', float(by_move['VERIFY']['ai_expl_presence_pct']) == 75.0, by_move['VERIFY']['ai_expl_presence_pct'], '75.0')
check('human_completeness_mean', float(by_src['human']['completeness_mean']) == 5.0, by_src['human']['completeness_mean'], '5.0')
check('ai_completeness_mean', float(by_src['ai']['completeness_mean']) == 4.0, by_src['ai']['completeness_mean'], '4.0')

fail = [c for c in checks if not c[1]]

lines = ['# Submission 60 Integrity Report', '']
for n, ok, got, exp in checks:
    status = 'PASS' if ok else 'FAIL'
    lines.append(f'- {status}: `{n}` (got={got}, expected={exp})')

lines.append('')
if fail:
    lines.append(f'Overall: FAIL ({len(fail)} checks failed)')
else:
    lines.append(f'Overall: PASS ({len(checks)} checks)')

OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(OUT)
print('pass' if not fail else 'fail')
