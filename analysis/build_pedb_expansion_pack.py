import csv
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
DOWNLOAD_XLSX = Path('/Users/abdulmohammad/Downloads/PEDB_Final_Spreadsheet__7__step5_done_fixed.xlsx')

PROMPTS_NEW = BASE / 'data' / 'templates' / 'pedb_prompts.csv'
SOURCES_NEW = BASE / 'data' / 'templates' / 'pedb_sources.csv'
HUMAN_NEW = BASE / 'data' / 'raw' / 'pedb_human_explanations_p21_p30.csv'
AI_NEW = BASE / 'data' / 'raw' / 'pedb_ai_explanations_p21_p30.csv'

OUT_PROMPTS = BASE / 'data' / 'templates' / 'pedb_prompts_30.csv'
OUT_SOURCES = BASE / 'data' / 'templates' / 'pedb_sources_30.csv'
OUT_EXPL = BASE / 'data' / 'processed' / 'pedb_explanations_90.csv'
OUT_OVERLAP = BASE / 'data' / 'annotations' / 'pedb_overlap_selection_24.csv'
OUT_QA = BASE / 'outputs' / 'expansion_qa_report.md'

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}


def _cell_value(cell):
    t = cell.attrib.get('t')
    if t == 'inlineStr':
        tnode = cell.find('m:is/m:t', NS)
        return tnode.text if tnode is not None else ''
    v = cell.find('m:v', NS)
    return v.text if v is not None else ''


def _col_idx(cell_ref: str) -> int:
    # e.g., "C12" -> 3
    letters = ''.join(ch for ch in cell_ref if ch.isalpha())
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch.upper()) - ord('A') + 1)
    return n


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
        for rel in rels.findall('m:Relationship', {'m':'http://schemas.openxmlformats.org/package/2006/relationships'}):
            if rel.attrib.get('Id') == rid:
                target = rel.attrib.get('Target')
                break
        if target is None:
            raise ValueError(f'Relationship target not found for {sheet_name}')

        target = target.lstrip('/')
        if target.startswith('xl/'):
            xml_path = target
        else:
            xml_path = 'xl/' + target
        root = ET.fromstring(zf.read(xml_path))

        rows = []
        max_col = 0
        for row in root.findall('m:sheetData/m:row', NS):
            vals = {}
            for c in row.findall('m:c', NS):
                ref = c.attrib.get('r', '')
                ci = _col_idx(ref)
                max_col = max(max_col, ci)
                vals[ci] = _cell_value(c)
            rows.append(vals)

        out = []
        for vals in rows:
            arr = [''] * max_col
            for ci, vv in vals.items():
                arr[ci - 1] = vv if vv is not None else ''
            out.append(arr)

        header = out[0]
        data = [dict(zip(header, r)) for r in out[1:]]
        return data


def normalize_topic(t: str) -> str:
    s = (t or '').strip().lower()
    if s in ('mechanics',):
        return 'Mechanics'
    if s in ('em', 'electricity & magnetism', 'electricity and magnetism'):
        return 'Electricity & Magnetism'
    if s in ('energy_work', 'thermo_waves', 'energy / work / thermo'):
        return 'Energy / Work / Thermo'
    return t or ''


def ensure_dirs():
    (BASE / 'data' / 'processed').mkdir(parents=True, exist_ok=True)


def main():
    ensure_dirs()

    # 1) Extract old workbook tables
    old_prompts = read_sheet_by_name(DOWNLOAD_XLSX, 'prompts')
    old_expl = read_sheet_by_name(DOWNLOAD_XLSX, 'explanations')

    # 2) Load new inputs
    with PROMPTS_NEW.open(newline='', encoding='utf-8') as f:
        new_prompts = list(csv.DictReader(f))
    with SOURCES_NEW.open(newline='', encoding='utf-8') as f:
        new_sources = list(csv.DictReader(f))
    with HUMAN_NEW.open(newline='', encoding='utf-8') as f:
        new_human = list(csv.DictReader(f))
    with AI_NEW.open(newline='', encoding='utf-8') as f:
        new_ai = list(csv.DictReader(f))

    # 3) Build combined prompts (30)
    prompts_rows = []
    for r in old_prompts:
        prompts_rows.append({
            'prompt_id': r.get('prompt_id','').strip(),
            'topic': normalize_topic(r.get('topic','')),
            'subtopic': r.get('subtopic','').strip(),
            'prompt_text': r.get('prompt_text','').strip(),
            'difficulty': 'intro',
            'target_audience': 'first_year_college',
            'notes': (r.get('notes') or '').strip(),
            'source_batch': 'legacy_20'
        })
    for r in new_prompts:
        prompts_rows.append({
            'prompt_id': r.get('prompt_id','').strip(),
            'topic': normalize_topic(r.get('topic','')),
            'subtopic': '',
            'prompt_text': r.get('prompt_text','').strip(),
            'difficulty': (r.get('difficulty') or 'intro').strip(),
            'target_audience': (r.get('target_audience') or 'first_year_college').strip(),
            'notes': (r.get('notes') or '').strip(),
            'source_batch': 'expansion_10'
        })

    # Dedup by prompt_id preserve order
    seen = set()
    prompts_30 = []
    for r in prompts_rows:
        pid = r['prompt_id']
        if not pid or pid in seen:
            continue
        seen.add(pid)
        prompts_30.append(r)

    # 4) Build combined explanations (90)
    expl_rows = []
    # old 60 from workbook
    for r in old_expl:
        if not (r.get('explanation_id') or '').strip():
            continue
        expl_rows.append({
            'explanation_id': (r.get('explanation_id') or '').strip(),
            'prompt_id': (r.get('prompt_id') or '').strip(),
            'topic': normalize_topic(r.get('topic','')),
            'source_type': (r.get('source_type') or '').strip(),
            'source_name': (r.get('source_name') or '').strip(),
            'source_url': (r.get('source_url') or '').strip(),
            'model_name': (r.get('model_name') or '').strip(),
            'generation_prompt': (r.get('generation_prompt') or '').strip(),
            'explanation_text': (r.get('explanation_text') or '').strip(),
            'word_count': int(float(r.get('word_count') or 0)) if (r.get('word_count') or '').strip() else 0,
            'annotation_status': (r.get('annotation_status') or '').strip(),
            'second_annotation_status': (r.get('second_annotation_status') or '').strip(),
            'physics_flag': (r.get('physics_flag') or '').strip(),
            'notes': (r.get('notes') or '').strip(),
            'batch': 'legacy_60'
        })

    source_by_prompt = {r['prompt_id']: r for r in new_sources}

    # new 10 human
    for r in new_human:
        pid = r['prompt_id'].strip()
        s = source_by_prompt.get(pid, {})
        text = (r.get('explanation_text') or '').strip()
        wc = len([w for w in text.split() if w])
        expl_rows.append({
            'explanation_id': (r.get('explanation_id') or '').strip(),
            'prompt_id': pid,
            'topic': normalize_topic(r.get('topic','')),
            'source_type': 'human',
            'source_name': (r.get('source_name') or s.get('source_name') or '').strip(),
            'source_url': (s.get('source_url_or_ref') or '').strip(),
            'model_name': '',
            'generation_prompt': '',
            'explanation_text': text,
            'word_count': wc,
            'annotation_status': 'pending',
            'second_annotation_status': '',
            'physics_flag': '',
            'notes': (r.get('notes') or '').strip(),
            'batch': 'expansion_30'
        })

    # new 20 ai
    for r in new_ai:
        expl_rows.append({
            'explanation_id': (r.get('explanation_id') or '').strip(),
            'prompt_id': (r.get('prompt_id') or '').strip(),
            'topic': normalize_topic(r.get('topic','')),
            'source_type': (r.get('source_type') or 'AI').strip(),
            'source_name': (r.get('source_name') or '').strip(),
            'source_url': (r.get('source_url') or '').strip(),
            'model_name': (r.get('model_name') or '').strip(),
            'generation_prompt': (r.get('generation_prompt') or '').strip(),
            'explanation_text': (r.get('explanation_text') or '').strip(),
            'word_count': int(float(r.get('word_count') or 0)) if (r.get('word_count') or '').strip() else 0,
            'annotation_status': (r.get('annotation_status') or 'pending').strip(),
            'second_annotation_status': (r.get('second_annotation_status') or '').strip(),
            'physics_flag': (r.get('physics_flag') or '').strip(),
            'notes': (r.get('notes') or '').strip(),
            'batch': 'expansion_30'
        })

    # dedup explanations by id
    seen_e = set()
    expl_90 = []
    for r in expl_rows:
        eid = r['explanation_id']
        if not eid or eid in seen_e:
            continue
        seen_e.add(eid)
        expl_90.append(r)

    # 5) Build combined sources (30 prompts)
    # legacy human source map from old explanations
    legacy_src = {}
    for r in expl_90:
        if r['batch'] == 'legacy_60' and r['source_type'].lower() == 'human':
            pid = r['prompt_id']
            if pid not in legacy_src:
                legacy_src[pid] = {
                    'prompt_id': pid,
                    'source_type': 'human',
                    'source_name': r['source_name'] or 'Legacy source',
                    'source_url_or_ref': r['source_url'] or '',
                    'license_or_usage_note': 'Legacy source from PEDB workbook; verify attribution before public release.',
                    'retrieval_date': '2026-04-10',
                    'notes': 'carried from legacy_60 explanations table'
                }

    sources_30 = []
    # old first in prompt order
    for p in prompts_30:
        pid = p['prompt_id']
        if pid in legacy_src:
            sources_30.append(legacy_src[pid])
        else:
            # new source row if exists
            nr = next((x for x in new_sources if x['prompt_id'] == pid), None)
            if nr:
                sources_30.append({
                    'prompt_id': nr['prompt_id'],
                    'source_type': nr['source_type'],
                    'source_name': nr['source_name'],
                    'source_url_or_ref': nr['source_url_or_ref'],
                    'license_or_usage_note': nr['license_or_usage_note'],
                    'retrieval_date': nr['retrieval_date'],
                    'notes': nr.get('notes','')
                })

    # 6) Create overlap selection (24 explanations = 8 prompts x 3 rows)
    # Stratified prompt pick: 3 mechanics, 3 E&M, 2 energy/thermo; include legacy+new
    selected_prompts = ['M02', 'M07', 'P21', 'E03', 'E06', 'P25', 'T03', 'P29']
    overlap = [r for r in expl_90 if r['prompt_id'] in selected_prompts]
    overlap.sort(key=lambda x: (selected_prompts.index(x['prompt_id']), x['explanation_id']))

    overlap_rows = []
    for r in overlap:
        overlap_rows.append({
            'explanation_id': r['explanation_id'],
            'prompt_id': r['prompt_id'],
            'topic': r['topic'],
            'source_type': r['source_type'],
            'source_name': r['source_name'],
            'model_name': r['model_name'],
            'word_count': r['word_count'],
            'annotator_2_status': 'pending',
            'notes': 'blind second-pass assignment',
            'explanation_text': r['explanation_text']
        })

    # 7) QA checks
    qa = {}
    qa['prompts_total'] = len(prompts_30)
    qa['explanations_total'] = len(expl_90)

    counts_by_prompt = Counter(r['prompt_id'] for r in expl_90)
    bad_prompt_counts = {k: v for k, v in counts_by_prompt.items() if v != 3}

    src_counts = Counter('human' if r['source_type'].lower() == 'human' else 'AI' for r in expl_90)
    topic_prompt_counts = Counter(r['topic'] for r in prompts_30)
    topic_expl_counts = Counter(r['topic'] for r in expl_90)

    missing_source_prompts = [p['prompt_id'] for p in prompts_30 if p['prompt_id'] not in {s['prompt_id'] for s in sources_30}]

    overlap_counts = {
        'rows': len(overlap_rows),
        'source': Counter('human' if r['source_type'].lower() == 'human' else 'AI' for r in overlap_rows),
        'topic': Counter(r['topic'] for r in overlap_rows),
        'prompts': Counter(r['prompt_id'] for r in overlap_rows)
    }

    # 8) Write outputs
    with OUT_PROMPTS.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['prompt_id','topic','subtopic','prompt_text','difficulty','target_audience','notes','source_batch'])
        w.writeheader(); w.writerows(prompts_30)

    with OUT_SOURCES.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['prompt_id','source_type','source_name','source_url_or_ref','license_or_usage_note','retrieval_date','notes'])
        w.writeheader(); w.writerows(sources_30)

    with OUT_EXPL.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['explanation_id','prompt_id','topic','source_type','source_name','source_url','model_name','generation_prompt','explanation_text','word_count','annotation_status','second_annotation_status','physics_flag','notes','batch'])
        w.writeheader(); w.writerows(expl_90)

    with OUT_OVERLAP.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['explanation_id','prompt_id','topic','source_type','source_name','model_name','word_count','annotator_2_status','notes','explanation_text'])
        w.writeheader(); w.writerows(overlap_rows)

    with OUT_QA.open('w', encoding='utf-8') as f:
        f.write('# PEDB Expansion QA Report\n\n')
        f.write(f"- prompts_total: {qa['prompts_total']}\n")
        f.write(f"- explanations_total: {qa['explanations_total']}\n")
        f.write(f"- source_counts: human={src_counts.get('human',0)}, AI={src_counts.get('AI',0)}\n")
        f.write(f"- bad_prompt_counts (must be empty): {bad_prompt_counts}\n")
        f.write(f"- missing_source_prompts (should be empty): {missing_source_prompts}\n\n")

        f.write('## Prompt Topic Counts\n')
        for k,v in sorted(topic_prompt_counts.items()):
            f.write(f"- {k}: {v}\n")
        f.write('\n## Explanation Topic Counts\n')
        for k,v in sorted(topic_expl_counts.items()):
            f.write(f"- {k}: {v}\n")

        f.write('\n## Overlap Selection (24 rows target)\n')
        f.write(f"- rows: {overlap_counts['rows']}\n")
        f.write(f"- source_counts: human={overlap_counts['source'].get('human',0)}, AI={overlap_counts['source'].get('AI',0)}\n")
        f.write('- topic_counts:\n')
        for k,v in sorted(overlap_counts['topic'].items()):
            f.write(f"  - {k}: {v}\n")
        f.write('- prompt_counts:\n')
        for k,v in sorted(overlap_counts['prompts'].items()):
            f.write(f"  - {k}: {v}\n")

    print(f'Wrote {OUT_PROMPTS}')
    print(f'Wrote {OUT_SOURCES}')
    print(f'Wrote {OUT_EXPL}')
    print(f'Wrote {OUT_OVERLAP}')
    print(f'Wrote {OUT_QA}')


if __name__ == '__main__':
    main()
