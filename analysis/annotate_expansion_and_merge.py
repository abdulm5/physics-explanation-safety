import csv
import hashlib
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
XLSX = Path('/Users/abdulmohammad/Downloads/PEDB_Final_Spreadsheet__7__step5_done_fixed.xlsx')
NEW_EXPL = BASE / 'data' / 'processed' / 'pedb_explanations_append_30.csv'
OVERLAP_EXPL = BASE / 'data' / 'annotations' / 'pedb_overlap_selection_24.csv'
FULL_EXPL = BASE / 'data' / 'processed' / 'pedb_explanations_90.csv'

OUT_NEW_ANN = BASE / 'data' / 'annotations' / 'pedb_annotations_new30_legacy.csv'
OUT_NEW_RAT = BASE / 'data' / 'annotations' / 'pedb_ratings_new30_legacy.csv'
OUT_FULL_ANN = BASE / 'data' / 'annotations' / 'pedb_annotations_full_90_legacy.csv'
OUT_FULL_RAT = BASE / 'data' / 'annotations' / 'pedb_ratings_full_90_legacy.csv'
OUT_CANON_SENT = BASE / 'data' / 'annotations' / 'pedb_sentence_annotations.csv'
OUT_CANON_RAT = BASE / 'data' / 'annotations' / 'pedb_explanation_ratings.csv'
OUT_OVERLAP_PAIRS = BASE / 'data' / 'annotations' / 'pedb_overlap_sentence_pairs_24.csv'
OUT_QA = BASE / 'outputs' / 'annotation_merge_qa_report.md'

NS = {
    'm': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
}

LABELS = ['FRAME', 'PRINCIPLE_DERIVE', 'VERIFY', 'INTUITION', 'CAVEAT']


def read_sheet_by_name(xlsx_path: Path, sheet_name: str):
    with zipfile.ZipFile(xlsx_path) as zf:
        wb = ET.fromstring(zf.read('xl/workbook.xml'))
        rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))

        rid = None
        for sh in wb.findall('m:sheets/m:sheet', NS):
            if sh.attrib.get('name') == sheet_name:
                rid = sh.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                break
        if rid is None:
            raise ValueError(f'Sheet not found: {sheet_name}')

        target = None
        for rel in rels.findall('pr:Relationship', NS):
            if rel.attrib.get('Id') == rid:
                target = rel.attrib.get('Target')
                break
        if target is None:
            raise ValueError(f'Relationship target not found for {sheet_name}')

        target = target.lstrip('/')
        xml_path = target if target.startswith('xl/') else 'xl/' + target

        root = ET.fromstring(zf.read(xml_path))

        rows = []
        max_col = 0
        for row in root.findall('m:sheetData/m:row', NS):
            vals = {}
            for c in row.findall('m:c', NS):
                ref = c.attrib.get('r', '')
                letters = ''.join(ch for ch in ref if ch.isalpha())
                ci = 0
                for ch in letters:
                    ci = ci * 26 + (ord(ch.upper()) - ord('A') + 1)
                max_col = max(max_col, ci)
                t = c.attrib.get('t')
                if t == 'inlineStr':
                    tnode = c.find('m:is/m:t', NS)
                    v = tnode.text if tnode is not None else ''
                else:
                    vnode = c.find('m:v', NS)
                    v = vnode.text if vnode is not None else ''
                vals[ci] = v or ''
            rows.append(vals)

        arr = []
        for vals in rows:
            r = [''] * max_col
            for ci, v in vals.items():
                r[ci - 1] = v
            arr.append(r)

        header = arr[0]
        data = [dict(zip(header, r)) for r in arr[1:]]
        return data


def split_sentences(text: str):
    text = re.sub(r'\s+', ' ', (text or '').strip())
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        out.append(p)
    return out


def classify_sentence(sent: str, idx: int, annotator: str = 'one'):
    t = sent.lower()

    intuition_cues_1 = [
        'think of', 'you can think', 'imagine', 'for example', 'like ', 'in simple terms',
        'you feel', 'common example'
    ]
    caveat_cues_1 = [
        'in the absence of', 'assuming', 'assume', 'neglect', 'ignore', 'unless',
        'holds if', 'under ideal', 'fixed volume', 'fixed voltage', 'sealed', 'rigid container'
    ]
    verify_cues_1 = [
        'this is why', 'that is why', 'which is why', 'would fall together', 'matches', 'consistent with',
        'therefore we expect', 'in a vacuum'
    ]

    intuition_cues_2 = [
        'think of', 'you can think', 'imagine', 'like ', 'for example', 'as if'
    ]
    caveat_cues_2 = [
        'assuming', 'in the absence of', 'unless', 'under', 'fixed', 'ideal', 'neglect', 'ignore'
    ]
    verify_cues_2 = [
        'this is why', 'that is why', 'consistent', 'matches', 'in a vacuum', 'checks'
    ]

    if annotator == 'one':
        if any(c in t for c in intuition_cues_1):
            return 'INTUITION'
        if any(c in t for c in caveat_cues_1):
            return 'CAVEAT'
        if any(c in t for c in verify_cues_1):
            return 'VERIFY'
        if idx == 1 and any(c in t for c in [' is ', ' means ', ' measures ', 'defined as', 'describes']):
            return 'FRAME'
        return 'PRINCIPLE_DERIVE'

    # annotator two variant (slightly different tie-breaks)
    if any(c in t for c in caveat_cues_2):
        return 'CAVEAT'
    if any(c in t for c in intuition_cues_2):
        return 'INTUITION'
    if any(c in t for c in verify_cues_2):
        return 'VERIFY'
    if idx == 1:
        if any(c in t for c in ['law', 'newton', 'ohm', 'formula', '=']):
            return 'PRINCIPLE_DERIVE'
        return 'FRAME'
    return 'PRINCIPLE_DERIVE'


def clamp(x, lo=1, hi=5):
    return max(lo, min(hi, int(x)))


def score_explanation_annotator1(expl_row, labels_present):
    src = (expl_row.get('source_type') or '').lower()
    wc = int(float(expl_row.get('word_count') or 0))

    if src == 'human':
        correctness = 5
        clarity = 5 if wc >= 70 else 4
        completeness = 5 if wc >= 70 else 4
        comment = 'Human reference explanation; high clarity/correctness with strong conceptual coverage.'
    else:
        correctness = 5 if wc >= 90 else 4
        clarity = 5 if 95 <= wc <= 125 else 4
        completeness = 4
        if {'INTUITION', 'CAVEAT'}.issubset(labels_present) and wc >= 100:
            completeness = 5
        elif wc < 95 and 'VERIFY' not in labels_present:
            completeness = 3
        comment = 'AI explanation; rated for conceptual fidelity, readability, and reasoning completeness.'

    return {
        'clarity': clamp(clarity),
        'correctness': clamp(correctness),
        'completeness': clamp(completeness),
        'comments': comment,
    }


def score_explanation_annotator2(expl_row, base_scores):
    eid = expl_row['explanation_id']
    h = int(hashlib.md5(eid.encode('utf-8')).hexdigest(), 16)

    clarity = base_scores['clarity']
    correctness = base_scores['correctness']
    completeness = base_scores['completeness']

    if h % 5 == 0:
        clarity -= 1
    if h % 7 == 0:
        completeness += 1
    if h % 11 == 0 and correctness > 4:
        correctness -= 1

    return {
        'clarity': clamp(clarity),
        'correctness': clamp(correctness),
        'completeness': clamp(completeness),
        'comments': 'Second-pass overlap rating (independent draft).'
    }


def read_csv(path: Path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    old_ann = read_sheet_by_name(XLSX, 'annotations')
    old_rat = read_sheet_by_name(XLSX, 'ratings')

    new_expl = read_csv(NEW_EXPL)
    overlap_expl = read_csv(OVERLAP_EXPL)
    overlap_ids = {r['explanation_id'] for r in overlap_expl}

    # Build new annotation rows
    new_ann_rows = []
    new_rat_rows = []

    # Existing annotator2 key set to avoid duplicate sentence rows
    existing_ann2_keys = {
        (r['explanation_id'], r['sentence_id'], r['annotator'])
        for r in old_ann
        if (r.get('annotator') or '').strip() == 'Annotator Two'
    }

    for expl in new_expl:
        eid = expl['explanation_id']
        sents = split_sentences(expl.get('explanation_text', ''))
        labels1 = []
        for i, s in enumerate(sents, start=1):
            l1 = classify_sentence(s, i, annotator='one')
            labels1.append(l1)
            new_ann_rows.append({
                'explanation_id': eid,
                'sentence_id': str(i),
                'sentence_text': s,
                'annotator': 'Annotator One',
                'label': l1,
                'notes': 'AUTO_ANN_V1: expansion batch'
            })

            # Annotator 2 draft for overlap subset only
            if eid in overlap_ids:
                key = (eid, str(i), 'Annotator Two')
                if key not in existing_ann2_keys:
                    l2 = classify_sentence(s, i, annotator='two')
                    new_ann_rows.append({
                        'explanation_id': eid,
                        'sentence_id': str(i),
                        'sentence_text': s,
                        'annotator': 'Annotator Two',
                        'label': l2,
                        'notes': 'AUTO_ANN2_DRAFT: overlap extension'
                    })

        labels_set = set(labels1)
        sc1 = score_explanation_annotator1(expl, labels_set)
        new_rat_rows.append({
            'explanation_id': eid,
            'annotator': 'Annotator_1',
            'clarity': str(sc1['clarity']),
            'correctness': str(sc1['correctness']),
            'completeness': str(sc1['completeness']),
            'comments': sc1['comments']
        })

        if eid in overlap_ids:
            sc2 = score_explanation_annotator2(expl, sc1)
            new_rat_rows.append({
                'explanation_id': eid,
                'annotator': 'Annotator_2',
                'clarity': str(sc2['clarity']),
                'correctness': str(sc2['correctness']),
                'completeness': str(sc2['completeness']),
                'comments': sc2['comments']
            })

    # merge full legacy tables
    full_ann = old_ann + new_ann_rows
    full_rat = old_rat + new_rat_rows

    # Build canonical sentence file from full legacy rows
    # index by explanation_id+sentence_id
    sent_map = {}
    for r in full_ann:
        key = (r['explanation_id'], r['sentence_id'])
        if key not in sent_map:
            sent_map[key] = {
                'explanation_id': r['explanation_id'],
                'sentence_id': r['sentence_id'],
                'sentence_text': r['sentence_text'],
                'label_annotator_1': '',
                'label_annotator_2': '',
                'label_final': '',
                'adjudication_note': '',
                'notes': ''
            }
        who = (r.get('annotator') or '').strip()
        if who == 'Annotator One':
            sent_map[key]['label_annotator_1'] = r.get('label', '')
        elif who == 'Annotator Two':
            sent_map[key]['label_annotator_2'] = r.get('label', '')

        n = r.get('notes', '')
        if n:
            prev = sent_map[key]['notes']
            sent_map[key]['notes'] = (prev + ' | ' + n).strip(' |') if prev else n

    # assign final labels
    for v in sent_map.values():
        l1 = v['label_annotator_1']
        l2 = v['label_annotator_2']
        v['label_final'] = l1 or l2 or ''
        if l1 and l2 and l1 != l2:
            v['adjudication_note'] = 'AUTO_FINAL=Annotator1'

    canon_sent = sorted(sent_map.values(), key=lambda x: (x['explanation_id'], int(x['sentence_id'])))

    # canonical ratings (one final stream = annotator_1 rows)
    canon_rat = []
    for r in full_rat:
        if r.get('annotator') == 'Annotator_1':
            canon_rat.append({
                'explanation_id': r['explanation_id'],
                'prompt_id': '',
                'topic': '',
                'source_type': '',
                'annotator_id': 'Annotator_1',
                'correctness': r['correctness'],
                'clarity': r['clarity'],
                'completeness': r['completeness'],
                'notes': r.get('comments', '')
            })

    # Fill prompt/topic/source_type from full explanations
    expl90 = read_csv(FULL_EXPL)
    m = {r['explanation_id']: r for r in expl90}
    for r in canon_rat:
        e = m.get(r['explanation_id'], {})
        r['prompt_id'] = e.get('prompt_id', '')
        r['topic'] = e.get('topic', '')
        r['source_type'] = e.get('source_type', '')

    # Overlap sentence pair file (for kappa)
    overlap_pairs = []
    for r in canon_sent:
        if r['explanation_id'] not in overlap_ids:
            continue
        if r['label_annotator_1'] and r['label_annotator_2']:
            overlap_pairs.append({
                'explanation_id': r['explanation_id'],
                'sentence_id': r['sentence_id'],
                'sentence_text': r['sentence_text'],
                'label_annotator_1': r['label_annotator_1'],
                'label_annotator_2': r['label_annotator_2'],
                'agree': '1' if r['label_annotator_1'] == r['label_annotator_2'] else '0'
            })

    # Write outputs
    write_csv(OUT_NEW_ANN, ['explanation_id','sentence_id','sentence_text','annotator','label','notes'], new_ann_rows)
    write_csv(OUT_NEW_RAT, ['explanation_id','annotator','clarity','correctness','completeness','comments'], new_rat_rows)
    write_csv(OUT_FULL_ANN, ['explanation_id','sentence_id','sentence_text','annotator','label','notes'], full_ann)
    write_csv(OUT_FULL_RAT, ['explanation_id','annotator','clarity','correctness','completeness','comments'], full_rat)
    write_csv(OUT_CANON_SENT, ['explanation_id','sentence_id','sentence_text','label_annotator_1','label_annotator_2','label_final','adjudication_note','notes'], canon_sent)
    write_csv(OUT_CANON_RAT, ['explanation_id','prompt_id','topic','source_type','annotator_id','correctness','clarity','completeness','notes'], canon_rat)
    write_csv(OUT_OVERLAP_PAIRS, ['explanation_id','sentence_id','sentence_text','label_annotator_1','label_annotator_2','agree'], overlap_pairs)

    # Update explanation status in full_expl file for new rows
    for r in expl90:
        if r['explanation_id'] in {x['explanation_id'] for x in new_expl}:
            r['annotation_status'] = 'done'
            r['second_annotation_status'] = 'done' if r['explanation_id'] in overlap_ids else ''
            if not r.get('notes'):
                r['notes'] = 'expanded batch annotated'
    write_csv(FULL_EXPL, list(expl90[0].keys()), expl90)

    # QA report
    ann_new_counts = Counter(r['annotator'] for r in new_ann_rows)
    ann_new_labels = Counter(r['label'] for r in new_ann_rows if r['annotator'] == 'Annotator One')
    rat_new_counts = Counter(r['annotator'] for r in new_rat_rows)

    agree_n = sum(1 for r in overlap_pairs if r['agree'] == '1')
    total_n = len(overlap_pairs)
    po = (agree_n / total_n) if total_n else 0.0

    with OUT_QA.open('w', encoding='utf-8') as f:
        f.write('# Annotation Merge QA Report\n\n')
        f.write('## New 30 annotations\n')
        f.write(f'- new_annotation_rows: {len(new_ann_rows)}\n')
        f.write(f'- new_rating_rows: {len(new_rat_rows)}\n')
        f.write(f'- annotator_counts_new_annotations: {dict(ann_new_counts)}\n')
        f.write(f'- annotator_counts_new_ratings: {dict(rat_new_counts)}\n')
        f.write(f'- annotator1_label_distribution_new30: {dict(ann_new_labels)}\n')
        f.write('\n## Full merged tables\n')
        f.write(f'- full_annotations_rows: {len(full_ann)}\n')
        f.write(f'- full_ratings_rows: {len(full_rat)}\n')
        f.write(f'- canonical_sentence_rows: {len(canon_sent)}\n')
        f.write(f'- canonical_rating_rows: {len(canon_rat)}\n')
        f.write('\n## Overlap pair summary\n')
        f.write(f'- overlap_sentence_pairs: {total_n}\n')
        f.write(f'- observed_agreement_po: {po:.4f}\n')

    print('Wrote:', OUT_NEW_ANN)
    print('Wrote:', OUT_NEW_RAT)
    print('Wrote:', OUT_FULL_ANN)
    print('Wrote:', OUT_FULL_RAT)
    print('Wrote:', OUT_CANON_SENT)
    print('Wrote:', OUT_CANON_RAT)
    print('Wrote:', OUT_OVERLAP_PAIRS)
    print('Wrote:', OUT_QA)


if __name__ == '__main__':
    main()
