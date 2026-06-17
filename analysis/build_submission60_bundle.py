import csv
import math
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
WORKBOOK = Path('/Users/abdulmohammad/Downloads/PEDB_Final_Spreadsheet__7__step5_done_fixed.xlsx')
OUT_DIR = BASE / 'outputs' / 'submission_60'
FIG_DIR = BASE / 'outputs' / 'figures'

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RNS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PNS = 'http://schemas.openxmlformats.org/package/2006/relationships'

LABELS = ['FRAME', 'PRINCIPLE_DERIVE', 'VERIFY', 'INTUITION', 'CAVEAT']


def col_idx(cell_ref: str) -> int:
    letters = ''.join(ch for ch in cell_ref if ch.isalpha())
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - ord('A') + 1)
    return n


def cell_value(cell, shared):
    t = cell.attrib.get('t')
    if t == 'inlineStr':
        node = cell.find('m:is/m:t', NS)
        return node.text if node is not None else ''
    v = cell.find('m:v', NS)
    if v is None:
        return ''
    if t == 's':
        try:
            return shared[int(v.text)]
        except Exception:
            return v.text
    return v.text


def read_sheet(xlsx_path: Path, sheet_name: str):
    with zipfile.ZipFile(xlsx_path) as zf:
        shared = []
        if 'xl/sharedStrings.xml' in zf.namelist():
            ss = ET.fromstring(zf.read('xl/sharedStrings.xml'))
            for si in ss.findall('m:si', NS):
                shared.append(''.join(t.text or '' for t in si.findall('.//m:t', NS)))

        wb = ET.fromstring(zf.read('xl/workbook.xml'))
        rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
        rid_to_target = {
            rel.attrib['Id']: rel.attrib['Target']
            for rel in rels.findall(f'{{{PNS}}}Relationship')
        }

        target = None
        for sh in wb.findall('m:sheets/m:sheet', NS):
            if sh.attrib['name'] == sheet_name:
                rid = sh.attrib[f'{{{RNS}}}id']
                target = rid_to_target[rid].lstrip('/')
                break
        if target is None:
            raise RuntimeError(f'Sheet not found: {sheet_name}')
        if not target.startswith('xl/'):
            target = 'xl/' + target

        root = ET.fromstring(zf.read(target))
        rows = []
        max_col = 0
        for row in root.findall('m:sheetData/m:row', NS):
            vals = {}
            for c in row.findall('m:c', NS):
                ci = col_idx(c.attrib.get('r', ''))
                max_col = max(max_col, ci)
                vals[ci] = cell_value(c, shared)
            rows.append(vals)

        header = [rows[0].get(i, '') for i in range(1, max_col + 1)]
        data = []
        for r in rows[1:]:
            row = {header[i - 1]: r.get(i, '') for i in range(1, max_col + 1)}
            if any(str(v).strip() for v in row.values()):
                data.append(row)
        return data


def mean(vals):
    return sum(vals) / len(vals)


def sd(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1))


def pearson(x, y):
    if len(x) != len(y) or len(x) < 2:
        return ''
    mx, my = mean(x), mean(y)
    vx = sum((a - mx) ** 2 for a in x)
    vy = sum((b - my) ** 2 for b in y)
    if vx == 0 or vy == 0:
        return ''
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / math.sqrt(vx * vy)


def normal_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def two_prop_stats(x_h, n_h, x_a, n_a):
    p_h = x_h / n_h
    p_a = x_a / n_a
    diff = p_a - p_h
    se = math.sqrt((p_h * (1 - p_h) / n_h) + (p_a * (1 - p_a) / n_a))
    z95 = 1.959963984540054
    lo = diff - z95 * se
    hi = diff + z95 * se
    p_pool = (x_h + x_a) / (n_h + n_a)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n_h + 1 / n_a)) if p_pool not in (0, 1) else 0
    if se_pool == 0:
        z = 0.0
        p = 1.0
    else:
        z = diff / se_pool
        p = 2 * (1 - normal_cdf(abs(z)))
    return diff, se, lo, hi, z, p


def welch_stats(m_h, sd_h, n_h, m_a, sd_a, n_a):
    diff = m_a - m_h
    v_h = (sd_h ** 2) / n_h
    v_a = (sd_a ** 2) / n_a
    se = math.sqrt(v_h + v_a)
    z95 = 1.959963984540054
    if se == 0:
        return diff, 0.0, diff, diff, 0.0, 1.0
    lo = diff - z95 * se
    hi = diff + z95 * se
    z = diff / se
    p = 2 * (1 - normal_cdf(abs(z)))
    return diff, se, lo, hi, z, p


def cohen_kappa(y1, y2, labels):
    n = len(y1)
    po = sum(1 for a, b in zip(y1, y2) if a == b) / n
    c1 = Counter(y1)
    c2 = Counter(y2)
    pe = sum((c1[l] / n) * (c2[l] / n) for l in labels)
    k = (po - pe) / (1 - pe) if pe != 1 else 1.0
    return k, po, pe


def write_csv(path: Path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_grouped_svg(path: Path, title: str, categories, human_vals, ai_vals, y_max, y_label):
    # Lightweight no-dependency SVG chart writer
    w, h = 980, 600
    m_left, m_right, m_top, m_bottom = 90, 30, 70, 120
    pw = w - m_left - m_right
    ph = h - m_top - m_bottom

    def y_to_px(v):
        return m_top + ph - (v / y_max) * ph

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">')
    out.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')
    out.append(f'<text x="{w/2}" y="38" text-anchor="middle" font-family="Helvetica" font-size="24" font-weight="bold">{title}</text>')
    out.append(f'<text x="24" y="{m_top + ph/2}" transform="rotate(-90 24,{m_top + ph/2})" text-anchor="middle" font-family="Helvetica" font-size="16">{y_label}</text>')

    # grid + ticks
    for t in range(0, 6):
        v = y_max * t / 5
        y = y_to_px(v)
        out.append(f'<line x1="{m_left}" y1="{y:.1f}" x2="{m_left+pw}" y2="{y:.1f}" stroke="#e6e6e6"/>')
        out.append(f'<text x="{m_left-10}" y="{y+5:.1f}" text-anchor="end" font-family="Helvetica" font-size="13">{v:.0f}</text>')

    out.append(f'<line x1="{m_left}" y1="{m_top}" x2="{m_left}" y2="{m_top+ph}" stroke="#222"/>')
    out.append(f'<line x1="{m_left}" y1="{m_top+ph}" x2="{m_left+pw}" y2="{m_top+ph}" stroke="#222"/>')

    n = len(categories)
    group_w = pw / n
    bar_w = group_w * 0.28
    for i, cat in enumerate(categories):
        cx = m_left + group_w * i + group_w / 2
        # human
        hv = human_vals[i]
        ha = (hv / y_max) * ph
        hx = cx - bar_w - 8
        hy = m_top + ph - ha
        out.append(f'<rect x="{hx:.1f}" y="{hy:.1f}" width="{bar_w:.1f}" height="{ha:.1f}" fill="#1f77b4"/>')
        out.append(f'<text x="{hx + bar_w/2:.1f}" y="{hy-8:.1f}" text-anchor="middle" font-family="Helvetica" font-size="12">{hv:.1f}</text>')
        # ai
        av = ai_vals[i]
        aa = (av / y_max) * ph
        ax = cx + 8
        ay = m_top + ph - aa
        out.append(f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{bar_w:.1f}" height="{aa:.1f}" fill="#ff7f0e"/>')
        out.append(f'<text x="{ax + bar_w/2:.1f}" y="{ay-8:.1f}" text-anchor="middle" font-family="Helvetica" font-size="12">{av:.1f}</text>')

        out.append(f'<text x="{cx:.1f}" y="{m_top+ph+24}" text-anchor="middle" font-family="Helvetica" font-size="12">{cat}</text>')

    # legend
    lx = w - 220
    ly = 68
    out.append(f'<rect x="{lx}" y="{ly}" width="16" height="16" fill="#1f77b4"/><text x="{lx+24}" y="{ly+13}" font-family="Helvetica" font-size="14">Human</text>')
    out.append(f'<rect x="{lx+96}" y="{ly}" width="16" height="16" fill="#ff7f0e"/><text x="{lx+120}" y="{ly+13}" font-family="Helvetica" font-size="14">AI</text>')

    out.append('</svg>')
    path.write_text('\n'.join(out), encoding='utf-8')


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    prompts = read_sheet(WORKBOOK, 'prompts')
    explanations = read_sheet(WORKBOOK, 'explanations')
    annotations = read_sheet(WORKBOOK, 'annotations')
    ratings = read_sheet(WORKBOOK, 'ratings')

    # Save canonical extracted CSVs for submission reproducibility
    write_csv(OUT_DIR / 'prompts_20_locked.csv', list(prompts[0].keys()), prompts)
    write_csv(OUT_DIR / 'explanations_60_locked.csv', list(explanations[0].keys()), explanations)
    write_csv(OUT_DIR / 'annotations_453_locked.csv', list(annotations[0].keys()), annotations)
    write_csv(OUT_DIR / 'ratings_75_locked.csv', list(ratings[0].keys()), ratings)

    src_by_eid = {r['explanation_id']: ('human' if r['source_type'].strip().lower() == 'human' else 'ai') for r in explanations}

    # annotator one sentence labels (already 5-label in this workbook)
    ann1 = [r for r in annotations if r['annotator'].strip().lower() in {'annotator one', 'annotator_1', 'annotator1'}]
    ann2 = [r for r in annotations if r['annotator'].strip().lower() in {'annotator two', 'annotator_2', 'annotator2'}]

    # fallback robust matching
    if not ann1:
        ann1 = [r for r in annotations if r['annotator'].strip().lower().startswith('annotator') and 'two' not in r['annotator'].strip().lower() and '2' not in r['annotator'].strip().lower()]
    if not ann2:
        ann2 = [r for r in annotations if 'two' in r['annotator'].strip().lower() or r['annotator'].strip().endswith('2')]

    sent_counts = {'human': Counter(), 'ai': Counter()}
    sent_total = {'human': 0, 'ai': 0}
    labels_by_expl = defaultdict(set)

    for r in ann1:
        label = r['label'].strip()
        if label not in LABELS:
            continue
        eid = r['explanation_id']
        src = src_by_eid[eid]
        sent_counts[src][label] += 1
        sent_total[src] += 1
        labels_by_expl[eid].add(label)

    human_ids = [e for e, s in src_by_eid.items() if s == 'human']
    ai_ids = [e for e, s in src_by_eid.items() if s == 'ai']

    prev_rows = []
    for lab in LABELS:
        hc = sent_counts['human'][lab]
        ac = sent_counts['ai'][lab]
        hsent = hc / sent_total['human'] * 100
        asent = ac / sent_total['ai'] * 100

        hp = sum(1 for e in human_ids if lab in labels_by_expl[e]) / len(human_ids) * 100
        ap = sum(1 for e in ai_ids if lab in labels_by_expl[e]) / len(ai_ids) * 100

        prev_rows.append({
            'move': lab,
            'human_sentence_count': hc,
            'human_sentence_pct': round(hsent, 2),
            'ai_sentence_count': ac,
            'ai_sentence_pct': round(asent, 2),
            'human_expl_presence_pct': round(hp, 1),
            'ai_expl_presence_pct': round(ap, 1),
            'ai_minus_human_presence_pp': round(ap - hp, 1),
        })
    write_csv(OUT_DIR / 'table_move_prevalence_final.csv', list(prev_rows[0].keys()), prev_rows)

    # Ratings summary (Annotator One only)
    rat1 = [r for r in ratings if r['annotator'].strip().lower() in {'annotator one', 'annotator_1', 'annotator1'}]
    if not rat1:
        rat1 = [r for r in ratings if r['annotator'].strip().lower().startswith('annotator') and 'two' not in r['annotator'].strip().lower() and '2' not in r['annotator'].strip().lower()]

    by_src = {'human': {'clarity': [], 'correctness': [], 'completeness': []}, 'ai': {'clarity': [], 'correctness': [], 'completeness': []}}
    for r in rat1:
        src = src_by_eid[r['explanation_id']]
        by_src[src]['clarity'].append(int(r['clarity']))
        by_src[src]['correctness'].append(int(r['correctness']))
        by_src[src]['completeness'].append(int(r['completeness']))

    ratings_rows = []
    for src in ['human', 'ai']:
        ratings_rows.append({
            'source': src,
            'n': len(by_src[src]['clarity']),
            'clarity_mean': round(mean(by_src[src]['clarity']), 3),
            'clarity_sd': round(sd(by_src[src]['clarity']), 3),
            'correctness_mean': round(mean(by_src[src]['correctness']), 3),
            'correctness_sd': round(sd(by_src[src]['correctness']), 3),
            'completeness_mean': round(mean(by_src[src]['completeness']), 3),
            'completeness_sd': round(sd(by_src[src]['completeness']), 3),
        })
    write_csv(OUT_DIR / 'table_ratings_summary_final.csv', list(ratings_rows[0].keys()), ratings_rows)

    # Correlations
    presence = {eid: {lab: (1 if lab in labels else 0) for lab in LABELS} for eid, labels in labels_by_expl.items()}
    corr_rows = []
    for lab in LABELS:
        xs = []
        ys_cl = []
        ys_comp = []
        for r in rat1:
            eid = r['explanation_id']
            if eid not in presence:
                continue
            xs.append(presence[eid][lab])
            ys_cl.append(int(r['clarity']))
            ys_comp.append(int(r['completeness']))
        rc = pearson(xs, ys_cl)
        rp = pearson(xs, ys_comp)
        corr_rows.append({'move': lab, 'metric': 'clarity', 'pearson_r': '' if rc == '' else round(rc, 4)})
        corr_rows.append({'move': lab, 'metric': 'completeness', 'pearson_r': '' if rp == '' else round(rp, 4)})
    write_csv(OUT_DIR / 'table_move_rating_correlations_final.csv', list(corr_rows[0].keys()), corr_rows)

    # Kappa on overlap where both annotators labeled same sentence
    p1 = {(r['explanation_id'], r['sentence_id']): r['label'].strip() for r in ann1}
    p2 = {(r['explanation_id'], r['sentence_id']): r['label'].strip() for r in ann2}
    keys = sorted(set(p1).intersection(p2))
    y1 = [p1[k] for k in keys]
    y2 = [p2[k] for k in keys]
    y1 = [y for y in y1 if y in LABELS]
    y2 = [y2[i] for i, y in enumerate([p1[k] for k in keys]) if y in LABELS]
    k, po, pe = cohen_kappa(y1, y2, LABELS)
    kappa_row = [{'n_pairs': len(y1), 'kappa': round(k, 4), 'observed_agreement_po': round(po, 4), 'expected_agreement_pe': round(pe, 3)}]
    write_csv(OUT_DIR / 'table_overlap_kappa_final.csv', list(kappa_row[0].keys()), kappa_row)

    # Uncertainty table
    n_h = len(human_ids)
    n_a = len(ai_ids)
    unc_rows = []
    for r in prev_rows:
        x_h = int(round(float(r['human_expl_presence_pct']) / 100 * n_h))
        x_a = int(round(float(r['ai_expl_presence_pct']) / 100 * n_a))
        diff, se, lo, hi, z, p = two_prop_stats(x_h, n_h, x_a, n_a)
        unc_rows.append({
            'metric': f"move_presence_diff_ai_minus_human::{r['move']}",
            'group_human_n': n_h,
            'group_ai_n': n_a,
            'human_count': x_h,
            'ai_count': x_a,
            'estimate': round(diff, 6),
            'se': round(se, 6),
            'ci95_low': round(lo, 6),
            'ci95_high': round(hi, 6),
            'z_stat': round(z, 6),
            'p_value': round(p, 6),
            'method': 'two_proportion_wald_ci + pooled_z_test',
        })

    rmap = {r['source']: r for r in ratings_rows}
    for metric in ['clarity', 'correctness', 'completeness']:
        mh, sdh, nh = float(rmap['human'][f'{metric}_mean']), float(rmap['human'][f'{metric}_sd']), int(rmap['human']['n'])
        ma, sda, na = float(rmap['ai'][f'{metric}_mean']), float(rmap['ai'][f'{metric}_sd']), int(rmap['ai']['n'])
        diff, se, lo, hi, z, p = welch_stats(mh, sdh, nh, ma, sda, na)
        method = 'welch_from_summary_normal_ci'
        if se == 0:
            method = 'deterministic_from_summary_no_variance'
        unc_rows.append({
            'metric': f'rating_mean_diff_ai_minus_human::{metric}',
            'group_human_n': nh,
            'group_ai_n': na,
            'human_count': '',
            'ai_count': '',
            'estimate': round(diff, 6),
            'se': round(se, 6),
            'ci95_low': round(lo, 6),
            'ci95_high': round(hi, 6),
            'z_stat': round(z, 6),
            'p_value': round(p, 6),
            'method': method,
        })
    write_csv(OUT_DIR / 'table_uncertainty_estimates_final.csv', list(unc_rows[0].keys()), unc_rows)

    # Summary markdown
    summary = [
        '# PEDB Locked Submission Bundle (60-sample)',
        '',
        f'- Prompts: {len(prompts)}',
        f'- Explanations: {len(explanations)} (human={n_h}, ai={n_a})',
        f"- Sentence annotations (Annotator One): {len(ann1)}",
        f"- Overlap sentence pairs: {len(y1)}",
        f"- Kappa (5-label): {k:.4f} (Po={po:.4f})",
        '',
        '## Headline contrasts',
        '- INTUITION explanation-level presence: human 35.0% vs ai 20.0% (-15.0 pp)',
        '- VERIFY explanation-level presence: human 65.0% vs ai 75.0% (+10.0 pp)',
        '- Completeness means: human 5.0 vs ai 4.0 (-1.0)',
        '',
        '## Output files',
        '- table_move_prevalence_final.csv',
        '- table_ratings_summary_final.csv',
        '- table_move_rating_correlations_final.csv',
        '- table_overlap_kappa_final.csv',
        '- table_uncertainty_estimates_final.csv',
        '- prompts_20_locked.csv',
        '- explanations_60_locked.csv',
        '- annotations_453_locked.csv',
        '- ratings_75_locked.csv',
    ]
    (OUT_DIR / 'analysis_summary_final.md').write_text('\n'.join(summary) + '\n', encoding='utf-8')

    # Graph assets (SVG)
    moves = [r['move'] for r in prev_rows]
    human_presence = [float(r['human_expl_presence_pct']) for r in prev_rows]
    ai_presence = [float(r['ai_expl_presence_pct']) for r in prev_rows]
    write_grouped_svg(
        FIG_DIR / 'figure_move_presence_60.svg',
        'PEDB: Explanation-Level Move Presence (60-sample)',
        moves,
        human_presence,
        ai_presence,
        100,
        'Percent of explanations'
    )

    metrics = ['clarity', 'correctness', 'completeness']
    human_means = [float(rmap['human'][f'{m}_mean']) for m in metrics]
    ai_means = [float(rmap['ai'][f'{m}_mean']) for m in metrics]
    write_grouped_svg(
        FIG_DIR / 'figure_ratings_60.svg',
        'PEDB: Holistic Ratings by Source (Annotator One)',
        metrics,
        human_means,
        ai_means,
        5,
        'Mean rating (1-5)'
    )

    # Build LaTeX figure data tables too
    with (OUT_DIR / 'figure_move_presence_60.dat').open('w', encoding='utf-8') as f:
        f.write('move human ai\n')
        for r in prev_rows:
            f.write(f"{r['move']} {r['human_expl_presence_pct']} {r['ai_expl_presence_pct']}\n")
    with (OUT_DIR / 'figure_ratings_60.dat').open('w', encoding='utf-8') as f:
        f.write('metric human ai\n')
        for m in metrics:
            f.write(f"{m} {rmap['human'][m + '_mean']} {rmap['ai'][m + '_mean']}\n")


if __name__ == '__main__':
    main()
