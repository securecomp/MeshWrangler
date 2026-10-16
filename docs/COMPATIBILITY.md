<!-- Document-ID: MeshWrangler/docs/COMPATIBILITY.md; Document-Version: 1.1.1; Previous-Document-Version: unversioned; Document-Revised: 2026-10-15 -->
# Compatibility

**MeshWrangler release:** v1.1.0  
**Explorer component:** v0.9.12

The configurations below describe observed or tested behavior, not a guarantee of compatibility with every version or device.

| Component | Version / environment | Verification |
|---|---|---|
| Processing pipeline | macOS Tahoe 26.5.1 | **Tested:** the master exporter, consolidator, and quality-review stages completed using three actual application backup snapshots: 229 unique nodes, 261 positions, and 390 telemetry records. |
| Python | Python 3; 3.14 observed in the development environment | Python 3 is required. The exact interpreter version used for the successful three-device run was not captured; Python 3.14 is **not** claimed as a separately validated configuration. Processing scripts use the Python standard library. |
| Explorer | v0.9.12; Safari 26.5 on macOS | **Tested:** interactive mapping in Online and Offline modes, pan, zoom, Fit controls, node selection and details, and online map-tile reload. Exhaustive filter testing has not been performed. |
| Source application | Meshtastic iOS application, 2.7.x family; 2.7.54 observed | Actual application-generated backup snapshots were processed successfully. A version-by-version application compatibility matrix has not been established. |
| iOS | Exact source-device version not recorded | No specific iOS-version compatibility claim. |
| Radio firmware | Not applicable to direct file processing | MeshWrangler processes exported application data; it does not communicate directly with radio firmware. |

## Compatibility boundaries

- Export compatibility depends on the structure of the application-generated database snapshots. Changes to that structure may require an exporter update.
- The Explorer reads generated JSON data. Its compatibility depends on that output format and browser capabilities, not on radio firmware.
- Offline mapping supports interaction without requesting new map tiles or terrain batches, but it is **not** a guaranteed zero-network mode; existing requests may finish, and initial map resources may require network access or a browser cache.
- Versions and combinations not specifically described as tested above remain **unverified**.

See [Processing](PROCESSING.md) for the workflow and [Explorer README](../explorer/EXPLORER_README.md) for viewer instructions.
