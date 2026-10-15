# Distribution manifest — MeshWrangler v1.1.0 (release candidate)

MeshWrangler includes four Python utilities under `src/`, the HTML Explorer v0.9.12 and `wrangle_it_v1.sh` launcher alongside the four Python scripts in `src/`, instructions, license, and third-party notices. This development archive includes SHA256SUMS for all distributed files except itself; final release checksums will be regenerated at release freeze.

The source distribution excludes all user datasets and working copies, including SQLite `.store` databases, `backup-index.json`, positions, messages, telemetry, CSV/JSON exports and identifying observations. Never commit private `NodeBackups/` content.

At final release packaging, generate `SHA256SUMS` covering every distributed file except itself; verify from the repository root with `shasum -a 256 -c SHA256SUMS`. This development archive contains a checked SHA256SUMS manifest; no final publication checksum has been issued. Checksums verify file integrity, not publisher authenticity. See `docs/COMPATIBILITY.md` for test status and `docs/ROADMAP.md` for unimplemented features.

## Component versions in assembled v1.1.0 candidate

Individual components retain stable filenames and version independently. Unmodified components retain their baseline versions.

| Component | Version | Baseline version | Change relative to v1.0.0 |
|---|---|---|---|
| `src/meshtastic_explorer.html` | v0.9.12 | v0.9.11 | Modified |
| `src/meshtastic_master_export_v1.py` | v1.1.0 | v1.0.0 | Modified |
| `src/meshtastic_snapshot_export_v2.py` | v2.1.0 | v2.0.0 | Modified |
| `src/meshtastic_consolidate_v2.py` | v2.0.0 | v2.0.0 | Unchanged |
| `src/meshtastic_quality_flags_review_v1.py` | v1.0.0 | v1.0.0 | Unchanged |
| `src/wrangle_it_v1.sh` | v1.0.0 | v1.0.0 | Unchanged |

Machine-readable hashes and predecessor versions: `COMPONENT_VERSIONS.json`.
