<!--
Document-ID: MeshWrangler/explorer/EXPLORER_README.md
Document-Version: 1.0.1
Document-Revised: 2026-10-15
Previous-Document-Version: unversioned (published v1.1.0)
-->

# MeshWrangler Explorer v0.9.12

A single-file, interactive viewer for examining historical mesh-network node observations, positions, activity, and related information. Part of **MeshWrangler — Historical Mesh Network Observation & Analysis**.

## Open and load

1. Open `src/meshtastic_explorer.html` in a compatible desktop browser. If you copied the six runnable files into your private working `NodeBackups/` collection, open `meshtastic_explorer.html` from there instead.
2. Select your private `NodeBackups/` collection using the folder picker, or select the required JSON files manually. The Explorer looks for consolidated data under `exports/master_data/` and validates the selected input structure.
3. Use node tables, filters, map markers, node details, movement views, and coverage overlays to examine the records. Coverage estimates and reception associations do **not** establish confirmed communication links.

The Explorer reads the selected node data locally and does not intentionally upload the complete dataset.

## Maps and network access

- **Online:** Street-map tiles may be retrieved from OpenStreetMap. Optional terrain lookup sends geographic coordinates to Open-Meteo. Leaflet assets may load from the unpkg CDN.
- **Offline:** Displays an interactive dark map with pan, zoom, Fit controls, markers, and node details. It prevents **new** street-tile and terrain requests while selected, but does not cancel requests already underway. Initial Leaflet assets may still require network access. **Offline is not a guaranteed zero-network mode.**

See [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) for service attribution, privacy considerations, and limitations.

## Compatibility

Explorer v0.9.12 was tested in Safari 26.5 for online and Offline map interaction, Fit Main/All, node selection and details, and online tile reload. Exhaustive filter coverage has not been established. For tested environments and source application details, see [`COMPATIBILITY.md`](../docs/COMPATIBILITY.md).

MeshWrangler is not affiliated with or endorsed by Meshtastic LLC or Apple Inc.
