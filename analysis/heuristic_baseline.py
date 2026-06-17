from __future__ import annotations
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('/Users/abdulmohammad/Projects/Physics&Ling')
ANNOT = BASE / 'outputs' / 'submission_60' / 'annotations_453_locked.csv'
OUT = BASE / 'outputs' / 'submission_60' / 'table_heuristic_baseline.csv'

LABELS = ['FRAME', 'PRINCIPLE_DERIVE', 'VERIFY', 'INTUITION', 'CAVEAT']

INTUITION_PATS = [
    r'\bfor example\b', r'\byou can think of\b', r'\bthink of it like\b',
    r'\blike water\b', r'\bsame idea\b', r'\bin everyday\b',
    r'\bcommon example\b', r'\bsuch as\b'
]
CAVEAT_PATS = [
    r'\bin reality\b', r'\bdoes not\b', r"\bdoesn't\b", r'\bnot mean\b',
    r'\bonly if\b', r'\bif we ignore\b', r'\bassuming\b', r'\bunless\b',
    r'\bprovided that\b'
]
VERIFY_PATS = [
    r'\bthis is why\b', r'\bthat is why\b', r'\bas a result\b',
    r'\btherefore\b', r'\bwhich means\b', r'\bso the\b', r'\bthis means\b'
]
FRAME_PATS = [
    r'\bin this situation\b', r'\bthe question\b', r'\bwhen an object\b',
    r'\bwhen current\b', r'\bwhen temperature\b', r'\bwhy does\b', r'\bwhy is\b'
]
PRINCIPLE_PATS = [
    r"\bnewton'?s\b", r"\bohm'?s law\b", r'\bideal gas law\b',
    r'\bconservation\b', r'\baccording to\b', r'\bthe equation\b',
    r'\bformula\b', r'\bforce equals\b', r'\bwork is\b', r'\bvoltage\b',
    r'\bpressure\b', r'\bacceleration\b'
]


def has_any(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def predict(text: str, sentence_id: str) -> str:
    t = text.strip().lower()
    if has_any(INTUITION_PATS, t):
        return 'INTUITION'
    if has_any(CAVEAT_PATS, t):
        return 'CAVEAT'
    if has_any(VERIFY_PATS, t):
        return 'VERIFY'
    if sentence_id == '1' and len(t.split()) < 25:
        return 'FRAME'
    if has_any(FRAME_PATS, t):
        return 'FRAME'
    if has_any(PRINCIPLE_PATS, t):
        return 'PRINCIPLE_DERIVE'
    return 'PRINCIPLE_DERIVE'

rows = []
with ANNOT.open() as f:
    for row in csv.DictReader(f):
        if row['annotator'] == 'Annotator One':
            rows.append(row)

conf = defaultdict(Counter)
correct = 0
for row in rows:
    gold = row['label']
    pred = predict(row['sentence_text'], row['sentence_id'])
    conf[gold][pred] += 1
    correct += int(gold == pred)

n = len(rows)
acc = correct / n
metrics = []
for label in LABELS:
    tp = conf[label][label]
    fp = sum(conf[g][label] for g in LABELS if g != label)
    fn = sum(conf[label][p] for p in LABELS if p != label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    metrics.append({
        'label': label,
        'n_gold': sum(conf[label].values()),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1': round(f1, 4),
    })

macro_f1 = sum(m['f1'] for m in metrics) / len(metrics)
rows_out = [
    {'metric': 'sentence_accuracy', 'value': round(acc, 4)},
    {'metric': 'macro_f1', 'value': round(macro_f1, 4)},
]
for m in metrics:
    rows_out.append({'metric': f"f1::{m['label']}", 'value': m['f1']})

with OUT.open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['metric', 'value'])
    writer.writeheader()
    writer.writerows(rows_out)

print(f'wrote {OUT}')
print(f'sentence_accuracy={acc:.4f}')
print(f'macro_f1={macro_f1:.4f}')
