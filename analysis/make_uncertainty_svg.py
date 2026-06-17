import csv
from pathlib import Path

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
INP = BASE / 'outputs' / 'submission_60' / 'table_uncertainty_estimates_final.csv'
OUT = BASE / 'outputs' / 'figures' / 'figure_uncertainty_60.svg'

rows = list(csv.DictReader(INP.open()))
# Keep key rows
want = [
    'move_presence_diff_ai_minus_human::INTUITION',
    'move_presence_diff_ai_minus_human::VERIFY',
    'rating_mean_diff_ai_minus_human::clarity',
    'rating_mean_diff_ai_minus_human::completeness',
]
sel = [r for r in rows if r['metric'] in want]

labels = {
    'move_presence_diff_ai_minus_human::INTUITION': 'INTUITION (AI-human, pp)',
    'move_presence_diff_ai_minus_human::VERIFY': 'VERIFY (AI-human, pp)',
    'rating_mean_diff_ai_minus_human::clarity': 'Clarity (AI-human)',
    'rating_mean_diff_ai_minus_human::completeness': 'Completeness (AI-human)',
}

# Convert move rows to percentage points for visual comparability
pts = []
for r in sel:
    m = r['metric']
    est = float(r['estimate'])
    lo = float(r['ci95_low'])
    hi = float(r['ci95_high'])
    if m.startswith('move_presence_diff_ai_minus_human'):
        est *= 100
        lo *= 100
        hi *= 100
    pts.append((labels[m], est, lo, hi, m))

# Draw simple horizontal CI plot
w, h = 980, 520
ml, mr, mt, mb = 260, 60, 70, 70
pw = w - ml - mr
ph = h - mt - mb

x_min, x_max = -45, 35

def xpx(v):
    return ml + (v - x_min) / (x_max - x_min) * pw

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">')
lines.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')
lines.append('<text x="490" y="34" text-anchor="middle" font-family="Helvetica" font-size="24" font-weight="bold">PEDB: Key Effect Estimates with 95% CIs</text>')

# zero line
zx = xpx(0)
lines.append(f'<line x1="{zx:.1f}" y1="{mt}" x2="{zx:.1f}" y2="{mt+ph}" stroke="#999" stroke-dasharray="4,4"/>')

# x ticks
for t in range(-40, 41, 10):
    x = xpx(t)
    lines.append(f'<line x1="{x:.1f}" y1="{mt+ph}" x2="{x:.1f}" y2="{mt+ph+6}" stroke="#333"/>')
    lines.append(f'<text x="{x:.1f}" y="{mt+ph+24}" text-anchor="middle" font-family="Helvetica" font-size="12">{t}</text>')

# axes
lines.append(f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" stroke="#333"/>')

row_gap = ph / (len(pts) + 1)
for i, (name, est, lo, hi, metric) in enumerate(pts, start=1):
    y = mt + i * row_gap
    x1 = xpx(lo)
    x2 = xpx(hi)
    xe = xpx(est)
    color = '#1f77b4' if 'move_presence' in metric else '#d62728'
    lines.append(f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="3"/>')
    lines.append(f'<line x1="{x1:.1f}" y1="{y-7:.1f}" x2="{x1:.1f}" y2="{y+7:.1f}" stroke="{color}" stroke-width="2"/>')
    lines.append(f'<line x1="{x2:.1f}" y1="{y-7:.1f}" x2="{x2:.1f}" y2="{y+7:.1f}" stroke="{color}" stroke-width="2"/>')
    lines.append(f'<circle cx="{xe:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>')
    lines.append(f'<text x="{ml-10}" y="{y+4:.1f}" text-anchor="end" font-family="Helvetica" font-size="13">{name}</text>')
    lines.append(f'<text x="{x2+8:.1f}" y="{y+4:.1f}" text-anchor="start" font-family="Helvetica" font-size="12">{est:.2f} [{lo:.2f}, {hi:.2f}]</text>')

lines.append(f'<text x="{ml+pw/2:.1f}" y="{h-18}" text-anchor="middle" font-family="Helvetica" font-size="14">Effect size (percentage points for move prevalence; raw scale for ratings)</text>')
lines.append('</svg>')

OUT.write_text('\n'.join(lines), encoding='utf-8')
print(OUT)
