# Distribution manifest — MeshWrangler v1.0.0

MeshWrangler includes four Python utilities under `src/`, the HTML Explorer v0.9.11 and `wrangle_it_v1.sh` launcher alongside the four Python scripts in `src/`, instructions, license, and third-party notices. Final release integrity checksums will be generated after the content freeze.

The source distribution excludes all user datasets and working copies, including SQLite `.store` databases, `backup-index.json`, positions, messages, telemetry, CSV/JSON exports and identifying observations. Never commit private `NodeBackups/` content.

At final release packaging, generate `SHA256SUMS` covering every distributed file except itself; verify from the repository root with `shasum -a 256 -c SHA256SUMS`. No final checksum manifest is present in this staging tree. Checksums verify file integrity, not publisher authenticity. See `docs/COMPATIBILITY.md` for test status and `docs/ROADMAP.md` for unimplemented features.
