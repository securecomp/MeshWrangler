<!--
Document-ID: MeshWrangler/docs/PROCESSING.md
Document-Version: 1.0.1
Document-Revised: 2026-10-15
Previous-Document-Version: unversioned (published v1.1.0)
-->

# Processing node data

MeshWrangler extracts and consolidates node observations from **working copies** of application-generated databases. It does not back up, restore, or modify the source application’s data. Preserve your originals separately.

## Prepare the working copy

1. Copy the application-generated `Documents/NodeBackups/` collection to a private working directory. Keep `backup-index.json`, its indexed subdirectories, and database files together. Do **not** rename or reorganize them.
2. The index identifies each source by its `backupPath`. Source directory names can be UUIDs or names such as `node-49131228`; an index entry may omit `deviceId`.
3. Keep each source's `Meshtastic.store` database with any associated `Meshtastic.store-wal` and `Meshtastic.store-shm` files when making the copy.
4. Copy the six runnable files from the repository's `src/` directory into the working `NodeBackups/` directory. Python 3 is required; see [Compatibility](COMPATIBILITY.md).

## Run processing

Open a terminal in the working `NodeBackups/` directory and run:

```bash
./wrangle_it_v1.sh
```

If the executable permission was lost while downloading or extracting, use `bash wrangle_it_v1.sh` instead. The launcher runs three stages in order, captures logs under `logs/`, and **stops before later stages if a stage fails**.

To run stages separately:

```bash
python3 ./meshtastic_master_export_v1.py
python3 ./meshtastic_consolidate_v2.py
python3 ./meshtastic_quality_flags_review_v1.py
```

1. **Export:** process the indexed source databases individually and write exports and `exports/master_manifest.json`. Successful source exports are retained even if another source fails. Existing validated exports may be skipped.
2. **Consolidate:** combine exports with source attribution under `exports/master_data/`. Missing source exports can prevent consolidation. See `exports/master_data/reconciliation_manifest.json` for details.
3. **Review:** report node-name variants and public-key conflicts from the consolidated dataset. Flags identify records for investigation; they do not automatically resolve conflicts.

## Explore results

Open [`src/meshtastic_explorer.html`](../src/meshtastic_explorer.html) from the repository, or the copied `meshtastic_explorer.html` in your working directory. Select the working `NodeBackups/` collection or the required consolidated JSON files. See the [Explorer guide](../explorer/EXPLORER_README.md).

## Data handling and privacy

- Keep original application databases untouched. Work from copies; do not discard database sidecars when they are needed for a consistent SQLite snapshot.
- `backup-index.json` and its `backupPath` entries originate with the application. MeshWrangler's output fields such as `backup_folder`, `backup_path`, and `backup_created_utc` preserve source attribution; they do not indicate a backup/restore feature.
- Generated exports, manifests, and logs may contain node identifiers, locations, and absolute local paths (including usernames). **Do not publish them without review and redaction.** The `.gitignore` helps avoid accidental additions but does not remove previously tracked files.
- Counts from multiple snapshots may overlap; they are not counts of independent radio receptions.
