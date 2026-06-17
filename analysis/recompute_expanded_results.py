import csv
import math
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
ANN = BASE / 'data' / 'annotations' / 'pedb_sentence_annotations.csv'
RAT = BASE / 'data' / 'annotations' / 'pedb_explanation_ratings.csv'
EXPL = BASE / 'data' / 'processed' / 'pedb_explanations_90.csv'
OVERLAP = BASE / 'data' / 'annotations' / 'pedb_overlap_sentence_pairs_24.csv'

OUT_PREV = BASE / 'outputs' / 'table_move_prevalence_expanded.csv'
OUT_RAT = BASE / 'outputs' / 'table_ratings_summary_expanded.csv'
OUT_CORR = BASE / 'outputs' / 'table_move_rating_correlations_expanded.csv'
OUT_KAPPA = BASE / 'outputs' / 'table_overlap_kappa_expanded.csv'
OUT_UNC = BASE / 'outputs' / 'table_uncertainty_estimates_expanded.csv'
OUT_SUM = BASE / 'outputs' / 'analysis_summary_expanded.md'

LABELS = ['FRAME', 'PRINCIPLE_DERIVE', 'VERIFY', 'INTUITION', 'CAVEAT']


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def mean(vals):
    return sum(vals)/len(vals) if vals else float('nan')


def sd(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    return math.sqrt(sum((x-m)**2 for x in vals)/(len(vals)-1))


def pearson(x,y):
    if len(x)!=len(y) or len(x)<2:
        return ''
    mx,my = mean(x), mean(y)
    vx = sum((a-mx)**2 for a in x)
    vy = sum((b-my)**2 for b in y)
    if vx==0 or vy==0:
        return ''
    cov = sum((a-mx)*(b-my) for a,b in zip(x,y))
    return cov / math.sqrt(vx*vy)


def normal_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def two_prop_stats(x_h,n_h,x_a,n_a):
    p_h = x_h/n_h
    p_a = x_a/n_a
    diff = p_a-p_h
    se = math.sqrt((p_h*(1-p_h)/n_h)+(p_a*(1-p_a)/n_a))
    z95 = 1.959963984540054
    lo = diff - z95*se
    hi = diff + z95*se
    p_pool = (x_h+x_a)/(n_h+n_a)
    se_pool = math.sqrt(p_pool*(1-p_pool)*(1/n_h+1/n_a)) if p_pool not in (0,1) else 0
    if se_pool==0:
        z=0.0; p=1.0
    else:
        z=diff/se_pool
        p=2*(1-normal_cdf(abs(z)))
    return diff,se,lo,hi,z,p


def welch_stats(m_h,sd_h,n_h,m_a,sd_a,n_a):
    diff = m_a - m_h
    v_h = (sd_h**2)/n_h
    v_a = (sd_a**2)/n_a
    se = math.sqrt(v_h+v_a)
    z95 = 1.959963984540054
    if se==0:
        return diff,0.0,diff,diff,0.0,1.0
    lo = diff - z95*se
    hi = diff + z95*se
    z = diff/se
    p = 2*(1-normal_cdf(abs(z)))
    return diff,se,lo,hi,z,p


def cohen_kappa(y1, y2, labels):
    n = len(y1)
    if n == 0:
        return float('nan'), 0.0, 0.0
    po = sum(1 for a,b in zip(y1,y2) if a==b)/n
    c1 = Counter(y1)
    c2 = Counter(y2)
    pe = 0.0
    for lab in labels:
        pe += (c1[lab]/n) * (c2[lab]/n)
    if pe == 1:
        k = 1.0
    else:
        k = (po - pe)/(1-pe)
    return k, po, pe


def main():
    ann = read_csv(ANN)
    rat = read_csv(RAT)
    expl = read_csv(EXPL)
    overlap = read_csv(OVERLAP)

    expl_map = {r['explanation_id']: r for r in expl}

    # Use label_final rows only
    ann_rows = []
    for r in ann:
        lab = (r.get('label_final') or '').strip()
        if lab not in LABELS:
            continue
        eid = r['explanation_id']
        src = (expl_map.get(eid,{}).get('source_type','') or '').lower()
        src = 'human' if src == 'human' else 'ai'
        ann_rows.append({'explanation_id':eid,'label':lab,'source':src})

    # sentence counts and distribution
    sent_counts = {'human':Counter(), 'ai':Counter()}
    sent_total = {'human':0, 'ai':0}
    for r in ann_rows:
        sent_counts[r['source']][r['label']] += 1
        sent_total[r['source']] += 1

    # explanation-level presence
    labels_by_expl = defaultdict(set)
    src_by_expl = {}
    for r in ann_rows:
        labels_by_expl[r['explanation_id']].add(r['label'])
        src_by_expl[r['explanation_id']] = r['source']

    expl_ids_h = [eid for eid,s in src_by_expl.items() if s=='human']
    expl_ids_a = [eid for eid,s in src_by_expl.items() if s=='ai']
    n_h, n_a = len(expl_ids_h), len(expl_ids_a)

    prev_rows = []
    for lab in LABELS:
        hc = sent_counts['human'][lab]
        ac = sent_counts['ai'][lab]
        h_pct = (hc/sent_total['human']*100) if sent_total['human'] else 0.0
        a_pct = (ac/sent_total['ai']*100) if sent_total['ai'] else 0.0

        h_expl = sum(1 for eid in expl_ids_h if lab in labels_by_expl[eid])
        a_expl = sum(1 for eid in expl_ids_a if lab in labels_by_expl[eid])
        h_expl_pct = (h_expl/n_h*100) if n_h else 0.0
        a_expl_pct = (a_expl/n_a*100) if n_a else 0.0

        prev_rows.append({
            'move': lab,
            'human_sentence_count': hc,
            'human_sentence_pct': round(h_pct,2),
            'ai_sentence_count': ac,
            'ai_sentence_pct': round(a_pct,2),
            'human_expl_presence_pct': round(h_expl_pct,1),
            'ai_expl_presence_pct': round(a_expl_pct,1),
            'ai_minus_human_presence_pp': round(a_expl_pct-h_expl_pct,1),
        })

    write_csv(OUT_PREV, list(prev_rows[0].keys()), prev_rows)

    # ratings summary (annotator_1 only)
    rat1 = [r for r in rat if r.get('annotator_id')=='Annotator_1']
    by_src = {'human':{'clarity':[],'correctness':[],'completeness':[]}, 'ai':{'clarity':[],'correctness':[],'completeness':[]}}
    for r in rat1:
        src = (r.get('source_type') or '').lower()
        src = 'human' if src=='human' else 'ai'
        by_src[src]['clarity'].append(int(r['clarity']))
        by_src[src]['correctness'].append(int(r['correctness']))
        by_src[src]['completeness'].append(int(r['completeness']))

    rat_rows = []
    for src in ['human','ai']:
        rat_rows.append({
            'source': src,
            'n': len(by_src[src]['clarity']),
            'clarity_mean': round(mean(by_src[src]['clarity']),3),
            'clarity_sd': round(sd(by_src[src]['clarity']),3),
            'correctness_mean': round(mean(by_src[src]['correctness']),3),
            'correctness_sd': round(sd(by_src[src]['correctness']),3),
            'completeness_mean': round(mean(by_src[src]['completeness']),3),
            'completeness_sd': round(sd(by_src[src]['completeness']),3),
        })

    write_csv(OUT_RAT, list(rat_rows[0].keys()), rat_rows)

    # correlations
    # build explanation-level feature matrix aligned with rat1
    presence = {}
    for eid, labs in labels_by_expl.items():
        presence[eid] = {lab: (1 if lab in labs else 0) for lab in LABELS}

    corr_rows = []
    for lab in LABELS:
        xs, ys_c, ys_comp = [], [], []
        for r in rat1:
            eid = r['explanation_id']
            if eid not in presence:
                continue
            xs.append(presence[eid][lab])
            ys_c.append(int(r['clarity']))
            ys_comp.append(int(r['completeness']))
        rc = pearson(xs, ys_c)
        rcomp = pearson(xs, ys_comp)
        corr_rows.append({'move':lab,'metric':'clarity','pearson_r': '' if rc=='' else round(rc,4)})
        corr_rows.append({'move':lab,'metric':'completeness','pearson_r': '' if rcomp=='' else round(rcomp,4)})

    write_csv(OUT_CORR, list(corr_rows[0].keys()), corr_rows)

    # kappa from overlap sentence pairs
    y1=[]; y2=[]
    for r in overlap:
        l1 = (r.get('label_annotator_1') or '').strip()
        l2 = (r.get('label_annotator_2') or '').strip()
        if l1 in LABELS and l2 in LABELS:
            y1.append(l1); y2.append(l2)

    k,po,pe = cohen_kappa(y1,y2,LABELS)
    krows=[{'n_pairs':len(y1),'kappa':round(k,4),'observed_agreement_po':round(po,4),'expected_agreement_pe':round(pe,4)}]
    write_csv(OUT_KAPPA, list(krows[0].keys()), krows)

    # uncertainty tables
    rat_map = {r['source']: r for r in rat_rows}
    unc_rows=[]
    for pr in prev_rows:
        lab=pr['move']
        x_h = int(round(float(pr['human_expl_presence_pct'])/100*n_h))
        x_a = int(round(float(pr['ai_expl_presence_pct'])/100*n_a))
        diff,se,lo,hi,z,p = two_prop_stats(x_h,n_h,x_a,n_a)
        unc_rows.append({
            'metric': f'move_presence_diff_ai_minus_human::{lab}',
            'group_human_n': n_h,
            'group_ai_n': n_a,
            'human_count': x_h,
            'ai_count': x_a,
            'estimate': round(diff,6),
            'se': round(se,6),
            'ci95_low': round(lo,6),
            'ci95_high': round(hi,6),
            'z_stat': round(z,6),
            'p_value': round(p,6),
            'method': 'two_proportion_wald_ci + pooled_z_test'
        })

    for metric in ['clarity','correctness','completeness']:
        mh=float(rat_map['human'][f'{metric}_mean']); sdh=float(rat_map['human'][f'{metric}_sd']); nh=int(rat_map['human']['n'])
        ma=float(rat_map['ai'][f'{metric}_mean']); sda=float(rat_map['ai'][f'{metric}_sd']); na=int(rat_map['ai']['n'])
        diff,se,lo,hi,z,p = welch_stats(mh,sdh,nh,ma,sda,na)
        unc_rows.append({
            'metric': f'rating_mean_diff_ai_minus_human::{metric}',
            'group_human_n': nh,
            'group_ai_n': na,
            'human_count': '',
            'ai_count': '',
            'estimate': round(diff,6),
            'se': round(se,6),
            'ci95_low': round(lo,6),
            'ci95_high': round(hi,6),
            'z_stat': round(z,6),
            'p_value': round(p,6),
            'method': 'welch_from_summary_normal_ci' if se>0 else 'deterministic_from_summary_no_variance'
        })

    write_csv(OUT_UNC, list(unc_rows[0].keys()), unc_rows)

    # summary md
    prev_map = {r['move']:r for r in prev_rows}
    with OUT_SUM.open('w', encoding='utf-8') as f:
        f.write('# PEDB Expanded Analysis Summary (90 explanations)\n\n')
        f.write(f'- Explanations: {n_h+n_a} (human={n_h}, ai={n_a})\n')
        f.write(f'- Sentence annotations used: {len(ann_rows)}\n')
        f.write(f'- Overlap sentence pairs for kappa: {len(y1)}\n')
        f.write(f'- Kappa (5-label): {k:.4f} (Po={po:.4f})\n\n')
        f.write('## Headline contrasts\n')
        f.write(f"- INTUITION explanation-level presence: human {prev_map['INTUITION']['human_expl_presence_pct']}% vs ai {prev_map['INTUITION']['ai_expl_presence_pct']}% ({prev_map['INTUITION']['ai_minus_human_presence_pp']} pp).\n")
        f.write(f"- VERIFY explanation-level presence: human {prev_map['VERIFY']['human_expl_presence_pct']}% vs ai {prev_map['VERIFY']['ai_expl_presence_pct']}% ({prev_map['VERIFY']['ai_minus_human_presence_pp']} pp).\n")
        f.write(f"- Ratings means (human): clarity {rat_map['human']['clarity_mean']}, correctness {rat_map['human']['correctness_mean']}, completeness {rat_map['human']['completeness_mean']}.\n")
        f.write(f"- Ratings means (ai): clarity {rat_map['ai']['clarity_mean']}, correctness {rat_map['ai']['correctness_mean']}, completeness {rat_map['ai']['completeness_mean']}.\n")

    print('Wrote', OUT_PREV)
    print('Wrote', OUT_RAT)
    print('Wrote', OUT_CORR)
    print('Wrote', OUT_KAPPA)
    print('Wrote', OUT_UNC)
    print('Wrote', OUT_SUM)


if __name__ == '__main__':
    main()
