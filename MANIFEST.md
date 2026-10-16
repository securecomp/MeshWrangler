<!-- Document-ID: MeshWrangler/MANIFEST.md; Document-Version: 1.1.1; Previous-Document-Version: unversioned; Document-Revised: 2026-10-15 -->
# Distribution manifest — MeshWrangler v1.1.0

MeshWrangler includes four Python utilities, the HTML Explorer v0.9.12, and the `wrangle_it_v1.sh` launcher under `src/`, plus instructions, license, and third-party notices. The published v1.1.0 release is frozen. The `main` branch may have subsequent documentation-only commits; `SHA256SUMS` describes the exact current source tree when updated together with those commits.

The source distribution excludes all user datasets and working copies, including SQLite `.store` databases, `backup-index.json`, positions, messages, telemetry, CSV/JSON exports and identifying observations. Never commit private `NodeBackups/` content.

`SHA256SUMS` covers every tracked distribution file except itself. Verify from the repository root with `shasum -a 256 -c SHA256SUMS`. Regenerate it after any source or documentation edit, before committing the updated source tree. Checksums verify file integrity, not publisher authenticity. See `docs/COMPATIBILITY.md` for test status and `docs/ROADMAP.md` for unimplemented features.

## Component versions in published v1.1.0

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
