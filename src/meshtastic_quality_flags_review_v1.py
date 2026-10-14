#!/usr/bin/env python3
"""Summarize Meshtastic consolidation quality flags (read-only)."""
import csv
from collections import Counter
from pathlib import Path

path = Path('exports/master_data/quality_flags.csv')
if not path.is_file():
    raise SystemExit(f'ERROR: Missing {path}. Run from the source collection directory after consolidation (existing layout: NodeBackups/).')

with path.open(newline='', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print('Columns:', list(rows[0]) if rows else [])
print('Flagged records:', len(rows))

for key in ('flag', 'flag_type', 'issue', 'type', 'category'):
    if rows and key in rows[0]:
        print('\nBy category:')
        for name, count in Counter(r[key] for r in rows).most_common():
            print(f'  {count:>4}  {name}')
        break

print('\nSample:')
for row in rows[:10]:
    print(row)
