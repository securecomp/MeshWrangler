# Data model and reconciliation semantics

Source schema (SwiftData/Core Data SQLite table names): `ZNODEINFOENTITY`, `ZUSERENTITY`, `ZPOSITIONENTITY`, `ZTELEMETRYENTITY`, `ZMESSAGEENTITY` and supporting tables. Node/user join `ZNODEINFOENTITY.ZUSER = ZUSERENTITY.Z_PK`; positions to node join `ZPOSITIONENTITY.ZNODEPOSITION = ZNODEINFOENTITY.Z_PK`; cached latest position field `ZLATESTPOSITIONCACHE` references position primary key. Meshtastic integer node numbers format `!%08x`; latitude/longitude stored as integer microdegrees times 10^7; Apple reference timestamps use 2001-01-01 UTC, with blank or zero handled as missing.

The Meshtastic iOS application generates `Documents/NodeBackups/backup-index.json` (private; not included), indexing its device database copies by UUID with fields including `backupPath`, `nodeNum`, `fileSize`, and `checksum`. MeshWrangler reads this application-provided index without requiring its names or directory structure to be changed. Treat this file as **private** (the repo excludes it). Indexed snapshots can contain broad app history beyond nodes heard by that particular radio. Source labeling thus denotes *which snapshot contained the record*, not proof of direct reception by that radio.

Consolidation produces `master_nodes`, `node_sources`, `positions`, `telemetry`, `sources`, `quality_flags` and `reconciliation_manifest` under `exports/master_data/` (CSV and JSON). Unique master nodes use numeric node identity; source records are retained separately; historic position and telemetry records remain attributed to the snapshot. Overlapping snapshots can contain repeated observations; counts must not be interpreted as independent receptions.

Quality review can report `name_variants` and `public_key_conflict`. These are findings, not automatic errors. Keys and names must be retained along with source identities. Downstream geography/timeline visualizers need their own provenance and timestamp quality controls.

Security/privacy: node names, public keys, IDs, map coordinates and message content are potentially identifying. Never publish real exports in the code GitHub repo.

Identifier origins differ: `backupPath` belongs to the application-provided `backup-index.json`; `backup_folder` is MeshWrangler-generated export/source-attribution metadata. Both are retained in their respective input/output formats; neither represents a MeshWrangler backup or recovery capability.
