#!/usr/bin/env python3
"""Consolidate Meshtastic Apple v2 master exports. Read-only input, standard library.

Run from the source collection directory (existing layout: NodeBackups/): python3 meshtastic_consolidate_v2.py
Creates exports/master_data/*.csv and *.json. No Excel dependency.
Does not modify input application databases or per-device exports.
"""
import argparse, collections, csv, hashlib, json, math, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

EPOCH=datetime(2001,1,1,tzinfo=timezone.utc)
HEXD=re.compile(r'^![0-9a-f]{8}$')

def hx(v):
    try: return '!%08x'%(int(v)&0xffffffff)
    except (ValueError,TypeError): return None

def iso(v):
    if v is None or v=='': return None
    try:
        v=float(v)
        if v==0 or not math.isfinite(v): return None
        return (EPOCH+timedelta(seconds=v)).isoformat()
    except (ValueError,TypeError,OverflowError): return None

def num(v):
    try:
        f=float(v)
        return f if math.isfinite(f) else None
    except (ValueError,TypeError): return None

def text(v): return str(v).strip() if v is not None else ''
def csv_cell(v):
    if isinstance(v,(dict,list)): return json.dumps(v,ensure_ascii=False,separators=(',',':'))
    if v is None:return ''
    # Avoid spreadsheet formula interpretation of untrusted node names in CSV clients.
    if isinstance(v,str) and v and v.lstrip().startswith(('=','+','-','@')): return "'"+v
    return v

def save_csv(p,rows,fields):
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for r in rows:w.writerow({k:csv_cell(r.get(k)) for k in fields})

def save_json(p,data):
    with p.open('w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')

def read_json(p):return json.loads(p.read_text(encoding='utf-8'))

def file_hash(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def valid_coordinate(lat,lon):
    return lat is not None and lon is not None and -90<=lat<=90 and -180<=lon<=180 and (lat!=0 or lon!=0)

def pick_recent(rows,field,sortfield):
    a=[r for r in rows if r.get(field) not in (None,'')]
    return max(a,key=lambda r:(str(r.get(sortfield) or ''),str(r.get('source_node_hex') or ''))).get(field) if a else None

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path('.'))
    ap.add_argument('--out',type=Path,default=None)
    args=ap.parse_args()
    root=args.root.resolve(); exp=root/'exports'; out=(args.out or exp/'master_data').resolve()
    if out == exp or out == root or exp not in out.parents:
        raise RuntimeError('Output directory must be a subdirectory within exports/')
    if not exp.is_dir():
        raise RuntimeError(f'Missing exports directory: {exp}')
    # Discover exported device directories dynamically from the filesystem.
    # A device is recognized by its export manifest, not by a configured name.
    manifests = {}
    for d in sorted(exp.iterdir()):
        if not d.is_dir() or d.resolve() == out or not (d/'manifest.json').is_file():
            continue
        m = read_json(d/'manifest.json')
        src = m.get('source', {})
        folder = src.get('backup_folder')
        node_hex = src.get('node_hex')
        if not folder or not node_hex:
            raise RuntimeError(f'Missing source identity in {d}/manifest.json')
        if folder in manifests:
            raise RuntimeError(f'Duplicate export source folder: {folder}')
        if not (root/folder/'Meshtastic.store').is_file():
            raise RuntimeError(f'Indexed source database not found: {root/folder}/Meshtastic.store')
        snapshot = m.get('snapshot', {})
        expected_hash = snapshot.get('sha256', '').lower()
        if not expected_hash or file_hash(root/folder/'Meshtastic.store').lower() != expected_hash:
            raise RuntimeError(f'Source database checksum mismatch: {folder}')
        manifests[folder] = (d, m)
    if not manifests:
        raise RuntimeError(f'No device exports containing manifest.json found under {exp}')
    source_dirs = {d.name for d in root.iterdir() if d.is_dir() and (d/'Meshtastic.store').is_file()}
    missing_exports = source_dirs - set(manifests)
    if missing_exports:
        raise RuntimeError('Source snapshot(s) lack a matching device export: ' + ', '.join(sorted(missing_exports)))
    # The existing input index (backup-index.json) is validation-only, if present; never drives discovery.
    index_path = root/'backup-index.json'
    indexed = read_json(index_path).get('entries', {}) if index_path.is_file() else {}
    for folder, (d, m) in manifests.items():
        item = indexed.get(folder)
        if item:
            if hx(item.get('nodeNum')) != m['source'].get('node_hex'):
                raise RuntimeError(f'Source-index node mismatch: {folder}')
            if item.get('checksum','').lower() != m['snapshot']['sha256'].lower():
                raise RuntimeError(f'Source-index checksum mismatch: {folder}')
    out.mkdir(parents=True,exist_ok=True)
    master_nodes=collections.defaultdict(list)
    node_sources=[]; positions=[]; telemetry=[]; sources=[]; warnings=[]
    for folder in sorted(manifests):
        d,m=manifests[folder];src=m['source'];source_hex=src['node_hex']
        if src.get('node_hex')!=source_hex:raise RuntimeError(f'Node identity mismatch {folder}')
        n=read_json(d/'nodes.json');p=read_json(d/'positions.json');t=read_json(d/'telemetry.json')
        expected=m.get('record_counts',{})
        for k,records in [('nodes_summary',n),('positions',p),('telemetry',t)]:
            if len(records)!=expected.get(k):raise RuntimeError(f'Count mismatch {folder}:{k}')
        source_name=src.get('long_name') or source_hex
        sources.append(dict(source_device=source_name,source_node_hex=source_hex,source_node_num=src['node_num'],backup_folder=folder,backup_created_utc=m['snapshot'].get('index_created_at_utc'),database_sha256=m['snapshot'].get('sha256'),nodes=len(n),positions=len(p),telemetry=len(t),export_dir=d.name))
        local_by_pk={}
        for r in n:
            node_hex=hx(r.get('node_num'))
            if not node_hex:
                warnings.append(dict(issue='missing_node_number',node_hex='',source_node_hex=source_hex,detail=f'node_pk={r.get("node_pk")}'));continue
            entry=dict(r,source_device=source_name,source_node_hex=source_hex,source_node_num=src['node_num'],backup_folder=folder,source_node_pk=r.get('node_pk'))
            entry['node_hex']=node_hex
            local_by_pk[r.get('node_pk')]=node_hex
            master_nodes[node_hex].append(entry)
            node_sources.append(entry)
        for dataset,output,table,default_field in [(p,positions,'position','ZNODEPOSITION'),(t,telemetry,'telemetry','ZNODETELEMETRY')]:
            for r in dataset:
                field=default_field
                link=r.get(field)
                if table=='telemetry' and field not in r:
                    candidates=[k for k in r if 'NODE' in k.upper() and k.upper() not in ('Z_PK','ZNODE')]
                    # Only use an unambiguous exact node FK; otherwise leave unresolved.
                    choices=[k for k in candidates if k.upper().endswith('NODETELEMETRY') or k.upper().endswith('TELEMETRYNODE')]
                    field=choices[0] if len(choices)==1 else None
                    link=r.get(field) if field else None
                node_hex=local_by_pk.get(link)
                enriched=dict(r,source_device=source_name,source_node_hex=source_hex,backup_folder=folder,node_hex=node_hex,relation_field=field if node_hex else None)
                if table=='position':
                    lat=num(r.get('ZLATITUDEI'));lon=num(r.get('ZLONGITUDEI'))
                    lat=lat/1e7 if lat is not None else None;lon=lon/1e7 if lon is not None else None
                    enriched.update(latitude=lat if valid_coordinate(lat,lon) else None,longitude=lon if valid_coordinate(lat,lon) else None,position_time_utc=iso(r.get('ZTIME')),rssi=r.get('ZRSSI'),snr=r.get('ZSNR'))
                    if not valid_coordinate(lat,lon):enriched['location_status']='invalid_or_missing'
                    else:enriched['location_status']='valid'
                else:
                    enriched['telemetry_time_utc']=iso(r.get('ZTIME'))
                output.append(enriched)
    # Source-specific counts are snapshots, not deduplicated transmissions.
    seen_positions=collections.defaultdict(list)
    for p in positions:
        if p.get('node_hex'):seen_positions[p['node_hex']].append(p)
        elif p.get('ZNODEPOSITION') is not None:warnings.append(dict(issue='unmatched_position',node_hex='',source_node_hex=p['source_node_hex'],detail=f'Z_PK={p.get("Z_PK")}'))
    per_node_telemetry=collections.Counter(t['node_hex'] for t in telemetry if t.get('node_hex'))
    master_list=[]
    for key,observations in sorted(master_nodes.items()):
        sources_here=sorted({r['source_node_hex'] for r in observations});names=sorted({text(r.get('long_name')) for r in observations if text(r.get('long_name'))})
        keys=sorted({text(r.get('public_key_hex')) for r in observations if text(r.get('public_key_hex'))})
        if len(keys)>1:warnings.append(dict(issue='public_key_conflict',node_hex=key,source_node_hex=','.join(sources_here),detail=f'{len(keys)} distinct keys'))
        if len(names)>1:warnings.append(dict(issue='name_variants',node_hex=key,source_node_hex=','.join(sources_here),detail=' | '.join(names)))
        ps=[p for p in seen_positions.get(key,[]) if p.get('location_status')=='valid']
        latest_p=max(ps,key=lambda x:(str(x.get('position_time_utc') or ''),str(x['source_node_hex'])),default=None)
        rssis=[num(r.get('rssi')) for r in observations];rssis=[x for x in rssis if x is not None and x!=0]
        snrs=[num(r.get('snr')) for r in observations];snrs=[x for x in snrs if x is not None]
        firsts=sorted(x['first_heard_utc'] for x in observations if x.get('first_heard_utc'))
        lasts=sorted(x['last_heard_utc'] for x in observations if x.get('last_heard_utc'))
        latest_node=max(observations,key=lambda x:str(x.get('last_heard_utc') or ''))
        master_list.append(dict(node_hex=key,node_num=latest_node.get('node_num'),long_name=pick_recent(observations,'long_name','last_heard_utc'),short_name=pick_recent(observations,'short_name','last_heard_utc'),hardware=pick_recent(observations,'hardware','last_heard_utc'),user_id=pick_recent(observations,'user_id','last_heard_utc'),first_heard_utc=firsts[0] if firsts else None,last_heard_utc=lasts[-1] if lasts else None,source_count=len(sources_here),source_devices='; '.join(sources_here),source_names='; '.join(sorted({r['source_device'] for r in observations})),snapshot_presence=len(observations),name_variants=' | '.join(names),public_key_variants=len(keys),rssi_min=min(rssis,default=None),rssi_max=max(rssis,default=None),rssi_mean=round(sum(rssis)/len(rssis),2) if rssis else None,snr_min=min(snrs,default=None),snr_max=max(snrs,default=None),snr_mean=round(sum(snrs)/len(snrs),2) if snrs else None,position_records=len(seen_positions.get(key,[])),valid_position_records=len(ps),latest_latitude=latest_p.get('latitude') if latest_p else None,latest_longitude=latest_p.get('longitude') if latest_p else None,latest_position_time_utc=latest_p.get('position_time_utc') if latest_p else None,telemetry_records=per_node_telemetry.get(key,0)))
    # Count validity metrics and provenance; no dedup of position/telemetry events without a stable packet ID.
    checks={'indexed_snapshots':len(indexed),'discovered_source_databases':len(source_dirs),'discovered_exports':len(manifests),'verified_snapshot_exports':len(sources),'node_source_rows':len(node_sources),'unique_nodes':len(master_list),'position_rows':len(positions),'telemetry_rows':len(telemetry),'linked_positions':sum(bool(r.get('node_hex')) for r in positions),'linked_telemetry':sum(bool(r.get('node_hex')) for r in telemetry),'valid_coordinates':sum(r.get('location_status')=='valid' for r in positions),'quality_flags':len(warnings)}
    overview=[{'metric':k,'value':v} for k,v in checks.items()]
    data={'overview':overview,'master_nodes':master_list,'node_sources':node_sources,'positions':positions,'telemetry':telemetry,'quality_flags':warnings,'sources':sources}
    for key,rows in data.items():
        save_json(out/f'{key}.json',rows)
        if rows:
            fields=list(dict.fromkeys(k for r in rows for k in r))
        else:fields=['empty']
        save_csv(out/f'{key}.csv',rows,fields)
    report={'export_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),'source_root':str(root),'counts':checks,'rules':{'node_identity':'Meshtastic 32-bit numeric node number, formatted !xxxxxxxx','names':'latest last_heard timestamp, variants retained','source_count':'distinct source snapshot node identifiers','rssi_snr':'snapshot node summary readings; NOT per-packet power series','positions':'preserve all observations, no deduplication of cross-snapshot copies','telemetry':'retain raw columns; node relation only if confidently identified','missing_position_time':'zero timestamp => null','coordinate_filter':'within latitude/longitude bounds and not (0,0)'},'cautions':['These snapshots may overlap: position and telemetry totals are not independent transmissions.','Raw telemetry field semantics depend on SwiftData schema; unknown relations remain null.','These outputs are for historical data analysis.'],'files':{}}
    for p in sorted(out.glob('*.csv'))+sorted(out.glob('*.json')):
        if p.name=='reconciliation_manifest.json':continue
        report['files'][p.name]={'sha256':file_hash(p),'bytes':p.stat().st_size}
    save_json(out/'reconciliation_manifest.json',report)
    print('Sources:',checks['verified_snapshot_exports'],'| Unique nodes:',checks['unique_nodes'],'| Source-node rows:',checks['node_source_rows'])
    print('Positions:',checks['position_rows'],'| Telemetry:',checks['telemetry_rows'],'| Flags:',checks['quality_flags'])
    print('Output:',out)

if __name__=='__main__':main()
