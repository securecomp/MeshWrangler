# MeshWrangler Explorer v0.9.11

An interactive, single-file HTML viewer for historical node records exported and consolidated from Meshtastic Apple application database snapshots. Part of **MeshWrangler — Historical Mesh Network Observation & Analysis**.

## Open and load

1. From the repository, open `src/meshtastic_explorer.html` in a compatible desktop browser. If the six runnable files were copied beside the app data in your private `NodeBackups/` working collection, open `meshtastic_explorer.html` there instead.
2. Choose your private source collection directory (currently named `NodeBackups/`) via the folder picker, or select the required JSON files manually.
3. The loader locates `exports/master_data/` within the selected folder and checks the input arrays and identities. The Explorer processes the selected NodeDB records locally; it does not intentionally upload the full dataset. Online maps request tiles for viewed areas, and optional terrain elevation requests send coordinates to Open-Meteo, as detailed below. Normal browser connection metadata is also visible to those services.
4. Use node tables, classification filters, location views, historical movement, and coverage overlays. Treat coverage and direct-reception associations as estimates rather than confirmed communication links.

## Online versus offline behavior

Node-record processing is local. Map tiles may be requested from OpenStreetMap, Leaflet library assets from unpkg, and optional terrain elevations from Open-Meteo; the latter sends geographic coordinates to the elevation API. These network requests are **not** equivalent to uploading a complete NodeDB dataset. See `../THIRD_PARTY_NOTICES.md` for providers, attribution, limitations, and privacy.

The existing **Offline coordinate plot** does *not* include offline map tiles or offline DEM terrain; it plots coordinates on a grid. A separately packaged regional offline basemap and elevation mode is future work, not a v0.9.11 feature.

## Compatibility and verification

Explorer v0.9.11 is the staged terminology revision. Explorer v0.9.10 was user-tested and accepted in Safari 26.5, including automatic street-map startup and historical NodeDB data loading. v0.9.11 was subsequently tested in Safari 26.5 with seven-device historical data (664 nodes, 6,502 positions, 7,086 telemetry). Map selection and both node-detail cards worked after refresh; exhaustive filter testing has not been claimed. Consult `../docs/COMPATIBILITY.md` for platform information.

This project is independent of Meshtastic LLC and Apple Inc.; see the repository README and third-party notices.
