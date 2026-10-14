#!/usr/bin/env python3
"""Batch-export indexed Meshtastic Apple application database snapshots.

Run from the source collection directory (currently NodeBackups/).
The input index is named backup-index.json for compatibility with existing collections.
Uses the already validated meshtastic_snapshot_export_v2.py unchanged.
Read-only on source snapshots. Each export is staged, validated, then published.
Requires only Python 3 standard library.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def slug(value):
    value = re.sub(r'[^A-Za-z0-9_-]+', '_', value or 'Unnamed').strip('_')
    return value[:70] or 'Unnamed'


def device_name(db, number):
    uri = db.resolve().as_uri() + '?mode=ro&immutable=1'
    with sqlite3.connect(uri, uri=True) as con:
        row = con.execute('''SELECT u.ZLONGNAME FROM ZNODEINFOENTITY AS n
            LEFT JOIN ZUSERENTITY AS u ON u.Z_PK = n.ZUSER
            WHERE n.ZNUM = ? LIMIT 1''', (number,)).fetchone()
    return row[0] if row and row[0] else 'Unnamed'


def read_manifest(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError, OSError):
        return None


def valid_existing(folder, entry, db_size, expected_sha):
    m = read_manifest(folder / 'manifest.json')
    if not m:
        return False
    src, snap, counts, checks = (m.get('source', {}), m.get('snapshot', {}),
                                 m.get('record_counts', {}), m.get('validation', {}))
    if src.get('backup_folder') != entry['backupPath'] or snap.get('sha256') != expected_sha:
        return False
    if snap.get('integrity') != 'ok' or snap.get('database_size') != db_size:
        return False
    if not (checks.get('source_node_found') and checks.get('node_number_unique')):
        return False
    # Validate exported JSON content as well as file presence before reusing it.
    # A damaged export must never be reported as a valid existing result.
    expected_counts = {
        'nodes': 'nodes_summary', 'nodes_raw': 'nodes_raw',
        'users_raw': 'users_raw', 'positions': 'positions',
        'telemetry': 'telemetry', 'messages': 'messages',
    }
    try:
        for name, count_key in expected_counts.items():
            if not (folder / f'{name}.csv').is_file():
                return False
            data = json.loads((folder / f'{name}.json').read_text(encoding='utf-8'))
            count = counts.get(count_key)
            if not isinstance(data, list) or not isinstance(count, int) or len(data) != count:
                return False
            if not all(isinstance(row, dict) for row in data):
                return False
    except (OSError, UnicodeError, ValueError, TypeError):
        return False
    return True


def ensure_under(parent, relative):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or len(rel.parts) != 1:
        raise ValueError(f'Unsafe source directory path: {relative!r}')
    return parent / rel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Source collection directory (default: cwd; existing layout: NodeBackups/)')
    parser.add_argument('--exporter', type=Path, default=None,
                        help='Location of meshtastic_snapshot_export_v2.py')
    parser.add_argument('--force', action='store_true', help='Rebuild exports into NEW versioned directories; never overwrite prior results')
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    index_path = root / 'backup-index.json'
    if not index_path.is_file():
        parser.error(f'Not found: {index_path}')
    exporter = (args.exporter or Path(__file__).resolve().parent / 'meshtastic_snapshot_export_v2.py').expanduser().resolve()
    if not exporter.is_file():
        parser.error(f'Exporter missing: {exporter} (use --exporter PATH)')
    entries = json.loads(index_path.read_text(encoding='utf-8')).get('entries', {})
    if not entries:
        parser.error('No entries in backup-index.json')
    destination = root / 'exports'
    destination.mkdir(exist_ok=True)
    results = []
    claimed = set()
    for device_id, entry in sorted(entries.items()):
        item = {'device_id': device_id, 'backup_path': entry.get('backupPath'),
                'node_num': entry.get('nodeNum'), 'status': 'failed', 'time_utc': utc_now()}
        try:
            folder = ensure_under(root, entry['backupPath'])
            if folder.name != device_id or entry.get('deviceId') != device_id:
                raise ValueError('Index device ID / source directory mismatch')
            db = folder / 'Meshtastic.store'
            if not db.is_file():
                raise FileNotFoundError(db)
            if db.stat().st_size != entry['fileSize']:
                raise ValueError('Source size differs from input index')
            actual_sha = sha256(db)
            if actual_sha.lower() != entry['checksum'].lower():
                raise ValueError('Source SHA-256 differs from input index')
            num = int(entry['nodeNum'])
            node_hex = f'{num & 0xffffffff:08x}'
            name = device_name(db, num)
            output_name = f'{slug(name)}_{node_hex}'
            if output_name in claimed:
                raise ValueError(f'Duplicate export directory name: {output_name}')
            claimed.add(output_name)
            out = destination / output_name
            item.update({'node_hex': '!' + node_hex, 'device_name': name,
                         'source_sha256': actual_sha, 'output_directory': str(out.relative_to(root))})
            if out.exists() and valid_existing(out, entry, db.stat().st_size, actual_sha) and not args.force:
                item['status'] = 'skipped_valid_existing'
                item['record_counts'] = read_manifest(out / 'manifest.json')['record_counts']
                print(f'SKIP   {name} (!{node_hex}): existing export validated', flush=True)
                results.append(item)
                continue
            if out.exists() and not args.force:
                raise FileExistsError(f'Existing directory not verified: {out}; preserved unchanged')
            if out.exists():
                timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                out = destination / f'{output_name}_rebuild_{timestamp}'
                if out.exists():
                    raise FileExistsError(out)
                item['output_directory'] = str(out.relative_to(root))
            staging = destination / f'.pending_{device_id}'
            if staging.exists():
                raise FileExistsError(f'Staging folder from previous run: {staging}; inspect before retrying')
            cmd = [sys.executable, str(exporter), str(db), '--index', str(index_path), '--out', str(staging)]
            print(f'EXPORT {name} (!{node_hex}) ...', flush=True)
            run = subprocess.run(cmd, text=True, capture_output=True)
            if run.returncode:
                raise RuntimeError(f'Exporter returned {run.returncode}: {(run.stderr or run.stdout).strip()}')
            if not valid_existing(staging, entry, db.stat().st_size, actual_sha):
                raise RuntimeError('Exporter completed but staging validation failed')
            manifest = read_manifest(staging / 'manifest.json')
            if manifest['source']['node_num'] != num:
                raise ValueError('Exported source identity differs from index')
            checks = manifest['validation']
            if checks['nodes_without_user_match'] != 0 or checks['positions_without_node_match'] != 0:
                raise ValueError(f'Exported relation validation failed: {checks}')
            staging.rename(out)
            item.update({'status': 'exported', 'record_counts': manifest['record_counts'],
                         'validation': checks})
            print(f'OK     {name}: {manifest["record_counts"]["nodes_summary"]} nodes, '
                  f'{manifest["record_counts"]["positions"]} positions, '
                  f'{manifest["record_counts"]["telemetry"]} telemetry', flush=True)
        except Exception as exc:
            item['error'] = str(exc)
            print(f'FAIL   {device_id}: {exc}', file=sys.stderr, flush=True)
        results.append(item)
    report = {'format_version': 1, 'created_utc': utc_now(), 'root': str(root),
              'source_index': 'backup-index.json', 'indexed_devices': len(entries),
              'status_counts': {s: sum(r['status'] == s for r in results)
                                for s in ('exported', 'skipped_valid_existing', 'failed')},
              'devices': results,
              'notes': ['Raw source databases have not been altered.',
                        'Source snapshots may contain overlapping app-wide histories; counts must not be summed as unique nodes.',
                        'Process working copies of application data; preserve originals independently.']}
    report_path = destination / 'master_manifest.json'
    if report_path.exists():
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        report_path = destination / f'master_manifest_{stamp}.json'
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'\nMaster manifest: {report_path}', flush=True)
    print('Summary: ' + ', '.join(f'{k}={v}' for k, v in report['status_counts'].items()), flush=True)
    return 1 if report['status_counts']['failed'] else 0

if __name__ == '__main__':
    sys.exit(main())
