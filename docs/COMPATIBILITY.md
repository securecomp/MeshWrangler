# Compatibility and test status

Status terms: **Accepted** means the user has validated the behavior; **Observed** means a version or environment is known but not an independently verified compatibility combination; **Pending** means no test claim is made.

| Component | Version / platform | Status and scope |
|---|---|---|
| Export/consolidation pipeline | Four distributed Python scripts (individual component versions in MANIFEST.md); MeshWrangler v1.1.0 candidate | Launcher and all three stages user-confirmed with three real app backups (229 unique nodes, 261 positions, 390 telemetry) on macOS for the SEC06_COMPAT candidate; earlier seven-device run also recorded; exact Python interpreter/build not independently captured |
| MeshWrangler Explorer | v0.9.12 | User-tested in Safari 26.5: Offline/Online pan, zoom, fit, node selection/details; online tile reload. Earlier v0.9.11 also tested with seven-device history; exhaustive filters not tested |
| Python | 3.14 on MacBook Neo | Installed/observed; exact original acceptance-test version pending |
| macOS | Tahoe 26.5.1 | Reported development environment; Safari 26.5 tested |
| Meshtastic Apple app | 2.7.x family; 2.7.54 observed | App-version-specific extraction regression matrix pending |
| Meshtastic radio firmware | 2.7.26 known firmware target | End-to-end compatibility not established; exporter reads application snapshot, not radio firmware directly |
| iOS | Version not captured | Pending |
| Browser | Safari 26.5 on macOS | Safari 26.5 user-tested with Explorer v0.9.12 and earlier v0.9.11 |

No untested combinations should be described as supported/validated. Database schema changes in later app versions may require exporter updates. The Explorer's compatibility boundary is exported JSON structure, not radio firmware.

Explorer v0.9.11 preserved v0.9.10 startup behavior and was subsequently field-tested in Safari 26.5. Interactive map/node cards passed following a refresh. Exhaustive filtering and all possible platform combinations were not tested.

Target assembled release: v1.1.0 (candidate, not published). This is not the published v1.0.0 baseline.
