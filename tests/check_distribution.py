#!/usr/bin/env python3
# MeshWrangler test-tool version: v1.0.1
"""MeshWrangler fail-closed distribution/history gate.
Usage: python3 tests/check_distribution.py CANDIDATE.zip IMMEDIATE_PREDECESSOR.zip [V1_BASELINE.zip]
The pinned predecessor SHA256 prevents accidentally testing against the wrong checkpoint.
Future candidates must be built with predecessor fields populated from the last accepted ZIP.
"""
import hashlib, json, re, sys, zipfile
from pathlib import Path
if len(sys.argv) not in (3,4):
    raise SystemExit('Usage: check_distribution.py candidate.zip immediate_predecessor.zip [v1_baseline.zip]')
root='MeshWrangler-main/'
def sha(b): return hashlib.sha256(b).hexdigest()
def triple(s):
    m=re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)',s)
    assert m, f'Invalid component version: {s}'
    return tuple(map(int,m.groups()))
with zipfile.ZipFile(sys.argv[1]) as candidate,zipfile.ZipFile(sys.argv[2]) as predecessor:
    paths={n[len(root):] for n in candidate.namelist() if n.startswith(root) and not n.endswith('/')}
    old={n[len(root):]:predecessor.read(n) for n in predecessor.namelist() if n.startswith(root) and not n.endswith('/')}
    def read(p): return candidate.read(root+p)
    inv=json.loads(read('COMPONENT_VERSIONS.json'))
    assert inv['predecessor_checkpoint']['sha256']==sha(Path(sys.argv[2]).read_bytes()), 'WRONG PREDECESSOR ZIP: SHA256 mismatch'
    old_inv=json.loads(old['COMPONENT_VERSIONS.json'])
    assert inv['assembled_release']=='v1.1.0'
    assert '# Distribution manifest — MeshWrangler v1.1.0' in read('MANIFEST.md').decode()
    assert '## v1.1.0 — Released' in read('CHANGELOG.md').decode()
    assert set(inv['components'])==set(old_inv['components']), 'Component inventory changed unexpectedly'
    assert inv.get('document_version'), 'Component inventory missing document revision'
    for doc in ('MANIFEST.md','CHANGELOG.md','docs/COMPATIBILITY.md'):
        assert f'Document-ID: MeshWrangler/{doc}; Document-Version:' in read(doc).decode(), f'Missing document revision: {doc}'
    for p,meta in inv['components'].items():
        assert p in old and p in paths, f'Component missing: {p}'
        prev=old_inv['components'][p];current=read(p)
        assert meta['predecessor_version']==prev['version'], f'Wrong predecessor version: {p}'
        assert meta['predecessor_sha256']==sha(old[p])==prev['sha256'], f'Wrong predecessor file hash: {p}'
        changed=current!=old[p]
        assert changed==meta['changed_from_predecessor'], f'Undeclared component change: {p}'
        assert sha(current)==meta['sha256'], f'Current component SHA256 mismatch: {p}'
        version=meta['version']; oldversion=prev['version']
        assert (triple(version)>triple(oldversion)) if changed else (version==oldversion), f'Version advancement/retention failure: {p}'
        source=current.decode('utf8')
        if p.endswith('.html'):
            assert f'<title>MeshWrangler Explorer · {version}</title>' in source, 'Explorer title mismatch'
            assert f'MeshWrangler Explorer <small>{version}</small>' in source, 'Explorer heading mismatch'
            assert f'<!-- MeshWrangler Explorer component version: {version} -->' in source, 'Explorer internal version mismatch'
        elif p.endswith('.py') and (changed or '# MeshWrangler component version:' in source):
            assert f'# MeshWrangler component version: {version}' in source, f'Python version mismatch: {p}'
        assert f'`{p}` | {version} | {meta["baseline_version"]}' in read('MANIFEST.md').decode(), f'Manifest missing component: {p}'
    hashes={}
    for line in read('SHA256SUMS').decode().splitlines():
        digest,path=line.split('  ',1)
        assert path not in hashes, f'Duplicate checksum: {path}'
        hashes[path]=digest
    assert set(hashes)==paths-{'SHA256SUMS'}, 'Distribution file inventory mismatch'
    for p,h in hashes.items(): assert sha(read(p))==h, f'Distribution checksum mismatch: {p}'
    assert candidate.getinfo(root+'src/wrangle_it_v1.sh').external_attr>>16 & 0o111, 'Launcher not executable'
    if len(sys.argv)==4:
        with zipfile.ZipFile(sys.argv[3]) as baseline:
            for p,meta in inv['components'].items():
                data=baseline.read(root+p)
                assert sha(data)==meta['baseline_sha256'], f'V1 baseline history mismatch: {p}'
print('PASS: immediate-predecessor pinned and matched; all component hashes/versions, labels, inventory, permissions verified')
