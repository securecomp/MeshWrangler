#!/usr/bin/env python3
"""Export ONE Meshtastic Apple 2.7.x SQLite snapshot, read-only.

No third-party dependencies. Exports node summary plus complete raw node,
user, position, telemetry, and message tables; preserves source metadata.
Do not use against a live SQLite store: immutable=1 ignores WAL changes.
"""
import argparse
import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

EPOCH = datetime(2001, 1, 1, tzinfo=timezone.utc)
TABLES = {
    'nodes_raw': 'ZNODEINFOENTITY', 'users_raw': 'ZUSERENTITY',
    'positions': 'ZPOSITIONENTITY', 'telemetry': 'ZTELEMETRYENTITY',
    'messages': 'ZMESSAGEENTITY',
}

def hex_id(n):
    return f'!{int(n) & 0xffffffff:08x}'

def apple_date(v):
    if v is None or not isinstance(v, (int, float)) or v == 0:
        return None
    try:
        return (EPOCH + timedelta(seconds=float(v))).isoformat()
    except (ValueError, OverflowError):
        return None

def convert(v):
    if isinstance(v, bytes):
        return {'hex': v.hex(), 'bytes': len(v)}
    return v

def dump_csv(path, data, fields):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for rec in data:
            writer.writerow({k: json.dumps(v, ensure_ascii=False, separators=(',', ':')) if isinstance(v, (dict, list)) else v for k, v in rec.items()})

def dump_json(path, data):
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def table_rows(con, table):
    fields = [x[1] for x in con.execute(f'PRAGMA table_info("{table}")')]
    if not fields:
        raise RuntimeError(f'Missing expected table: {table}')
    rows = []
    for row in con.execute(f'SELECT * FROM "{table}" ORDER BY Z_PK'):
        r = {field: convert(row[field]) for field in fields}
        for field in fields:
            if field in ('ZFIRSTHEARD', 'ZLASTHEARD', 'ZTIME', 'ZLASTMESSAGE', 'ZSESSIONEXPIRATION'):
                r[field + '_UTC'] = apple_date(row[field])
        rows.append(r)
    return rows, list(rows[0]) if rows else fields

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('database', type=Path)
    ap.add_argument('--index', type=Path, help='Source index (existing filename: backup-index.json), normally in the parent source collection')
    ap.add_argument('--out', type=Path, help='output directory (default: sibling export_<source-id>)')
    args = ap.parse_args()
    db = args.database.expanduser().resolve()
    if not db.is_file():
        ap.error(f'Missing database {db}')
    if db.name != 'Meshtastic.store':
        ap.error('Expected a Meshtastic.store snapshot')
    entry_id = db.parent.name
    idx_path = args.index or db.parent.parent / 'backup-index.json'
    idx_path = idx_path.expanduser().resolve()
    if not idx_path.is_file():
        ap.error(f'Missing source index: {idx_path} (provide --index)')
    index = json.loads(idx_path.read_text(encoding='utf-8'))
    entry = index.get('entries', {}).get(entry_id)
    if entry is None:
        ap.error(f'Source directory {entry_id} is not in {idx_path}')
    source_num = int(entry['nodeNum'])
    source_hex = hex_id(source_num)
    actual_sha = sha256(db)
    expected_sha = entry.get('checksum')
    expected_size = entry.get('fileSize')
    if expected_size is not None and db.stat().st_size != expected_size:
        raise RuntimeError('Database size differs from index!')
    if expected_sha and actual_sha.lower() != expected_sha.lower():
        raise RuntimeError('Database SHA-256 differs from source index; check the working copy.')
    out = (args.out or db.parent / f'export_{source_hex[1:]}').expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db.as_uri() + '?mode=ro&immutable=1', uri=True)
    con.row_factory = sqlite3.Row
    try:
        integrity = con.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity != 'ok':
            raise RuntimeError(f'Integrity check failed: {integrity}')
        raw = {}
        counts = {}
        for key, table in TABLES.items():
            rows, columns = table_rows(con, table)
            raw[key] = rows
            counts[key] = len(rows)
            dump_json(out / f'{key}.json', rows)
            dump_csv(out / f'{key}.csv', rows, columns)

        users = {x['Z_PK']: x for x in raw['users_raw']}
        positions = {}
        for x in raw['positions']:
            positions.setdefault(x['ZNODEPOSITION'], []).append(x)
        by_pk = {x['Z_PK']: x for x in raw['positions']}
        summary = []
        for n in raw['nodes_raw']:
            user = users.get(n.get('ZUSER'))
            p = by_pk.get(n.get('ZLATESTPOSITIONCACHE'))
            if p is None and positions.get(n['Z_PK']):
                p = max(positions[n['Z_PK']], key=lambda x: ((x.get('ZTIME') or 0), x['Z_PK']))
            num = n.get('ZNUM')
            row = {
                'source_device_id': entry_id, 'source_node_num': source_num,
                'source_node_hex': source_hex, 'node_pk': n['Z_PK'],
                'node_num': num, 'node_hex': hex_id(num) if num is not None else None,
                'long_name': user.get('ZLONGNAME') if user else None,
                'short_name': user.get('ZSHORTNAME') if user else None,
                'hardware': user.get('ZHWMODEL') if user else None,
                'user_id': user.get('ZUSERID') if user else None,
                'first_heard_utc': apple_date(n.get('ZFIRSTHEARD')),
                'last_heard_utc': apple_date(n.get('ZLASTHEARD')),
                'rssi': n.get('ZRSSI'), 'snr': n.get('ZSNR'),
                'hops_away': n.get('ZHOPSAWAY'), 'via_mqtt': n.get('ZVIAMQTT'),
                'position_time_utc': apple_date(p.get('ZTIME')) if p else None,
                'latitude': p['ZLATITUDEI'] / 1e7 if p and p.get('ZLATITUDEI') is not None else None,
                'longitude': p['ZLONGITUDEI'] / 1e7 if p and p.get('ZLONGITUDEI') is not None else None,
                'altitude': p.get('ZALTITUDE') if p else None,
                'public_key_hex': user['ZPUBLICKEY']['hex'] if user and isinstance(user.get('ZPUBLICKEY'), dict) else None,
            }
            summary.append(row)
        dump_csv(out / 'nodes.csv', summary, list(summary[0]) if summary else [])
        dump_json(out / 'nodes.json', summary)
        counts['nodes_summary'] = len(summary)
        source = next((r for r in summary if r['node_num'] == source_num), None)
        # Counts and relationships are validated; unmatched records are still exported.
        node_pks = {n['Z_PK'] for n in raw['nodes_raw']}
        checks = {
            'nodes_without_user_match': sum(bool(n['ZUSER']) and n['ZUSER'] not in users for n in raw['nodes_raw']),
            'positions_without_node_match': sum(bool(p.get('ZNODEPOSITION')) and p['ZNODEPOSITION'] not in node_pks for p in raw['positions']),
            'node_number_unique': len({n['ZNUM'] for n in raw['nodes_raw']}) == counts['nodes_raw'],
            'source_node_found': source is not None,
        }
        if not checks['source_node_found'] or not checks['node_number_unique']:
            raise RuntimeError(f'Identity checks failed: {checks}')
        manifest = {
            'export_version': 2, 'exported_at_utc': datetime.now(timezone.utc).isoformat(),
            'source': {'backup_folder': entry_id, 'device_id': entry['deviceId'],
                       'node_num': source_num, 'node_hex': source_hex,
                       'long_name': source['long_name'], 'short_name': source['short_name'],
                       'hardware': source['hardware']},
            'snapshot': {'database_name': db.name, 'database_size': db.stat().st_size,
                         'sha256': actual_sha, 'index_recorded_sha256': expected_sha,
                         'index_created_at_utc': apple_date(entry.get('createdAt')),
                         'integrity': integrity},
            'record_counts': counts, 'validation': checks,
            'notes': ['Raw table exports retain original database column names and relationships.',
                      'Binary fields appear as hex and byte length.',
                      'Full positions and telemetry are exported even when their node relationships differ.',
                      'Messages may include private content; protect export directory.',
                      'Process working copies of application data; preserve originals independently.']
        }
        dump_json(out / 'manifest.json', manifest)
        print(f'Source: {source["long_name"]} ({source_hex}) / {entry_id}')
        print(f'Integrity: {integrity} | SHA-256 matches index: yes')
        print('Counts:', ', '.join(f'{k}={v}' for k, v in counts.items()))
        print('Validation:', checks)
        print(f'Output: {out}')
    finally:
        con.close()

if __name__ == '__main__':
    main()
