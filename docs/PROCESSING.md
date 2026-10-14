# Processing historical node observations

MeshWrangler reads **working copies** of application databases from multiple device/application sources, exports records, consolidates the data with source attribution, and produces quality reports for analysis. Preserve your original data independently.

## Existing input layout

The Meshtastic iOS application supplies the `Documents/NodeBackups/` directory structure, including `backup-index.json` (with its `backupPath` field) and indexed `<UUID>/Meshtastic.store` device database files. Associated SQLite `Meshtastic.store-wal` and `Meshtastic.store-shm` files may also be present. Copy the application-provided structure intact for analysis; MeshWrangler reads it without requiring renames or reorganization. Within that *working copy*, MeshWrangler may add its scripts, logs, `exports/`, and other processing outputs. `backup_folder` is an output/source-attribution field created by MeshWrangler, not part of the supplied index. None of these names implies a MeshWrangler backup or recovery feature.

## Run the three processing stages

Copy the six working files from `src/` into the same source collection directory, then open a terminal there. The source index `backup-index.json` and indexed device subdirectories stay in that directory. Python 3 is required; see [compatibility](COMPATIBILITY.md). Run `./wrangle_it_v1.sh` (or `bash wrangle_it_v1.sh` if download/extraction stripped executable permissions). The equivalent manual stages are:

```bash
python3 ./meshtastic_master_export_v1.py
python3 ./meshtastic_consolidate_v2.py
python3 ./meshtastic_quality_flags_review_v1.py
```

1. **Extraction:** process indexed databases independently. Successful results are retained; existing validated exports may be skipped. An individual source failure is recorded while other sources continue processing. The command can return nonzero when one or more sources fail.
2. **Consolidation:** build a source-attributed master dataset under `exports/master_data/`. The current consolidator checks that discovered sources have corresponding exports; a missing device export can prevent a complete master consolidation. Previously successful individual exports remain available.
3. **Quality review:** report node-name variants and public-key conflicts from the consolidated output. Run this stage when a master dataset is available.

Review `exports/master_manifest.json` for extraction results and `exports/master_data/reconciliation_manifest.json` for consolidation results. These manifests contain local absolute source paths (`root` and `source_root`), potentially identifying local usernames and directories: keep them private or redact before sharing. Observations may overlap across source snapshots; record counts are not independent RF receptions. Launcher logs under `logs/` may also include absolute paths, device identifiers, and error details. The repository `.gitignore` excludes `logs/` and `*.log`; keep generated logs private and check already-tracked repository files separately before publication.

The original `.store` database files are read as inputs and should not be edited in place. Work on copies of source application data. If SQLite write-ahead-log (`-wal`) and shared-memory (`-shm`) sidecars are relevant to a copied database, keep the set consistent when creating the working copy.

## Inspect the results

From the repository, open [`../src/meshtastic_explorer.html`](../src/meshtastic_explorer.html); if following the working-copy setup above, open `meshtastic_explorer.html` from the copied `NodeBackups/` directory instead. Select the source collection directory or the required consolidated JSON files. The Explorer uses the outputs in `exports/master_data/`.

## Legacy input identifiers

Application-provided input names include `NodeBackups/`, `backup-index.json`, and its `backupPath` field. MeshWrangler-generated output metadata includes `backup_folder` and `backup_created_utc` (and `backup_path` in its master processing report). The current readers and outputs preserve these names to process existing collections and results; no input-structure changes are required. These identifiers are not backup/recovery features.
