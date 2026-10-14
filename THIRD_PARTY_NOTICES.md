# Third-party notices and acknowledgements

MeshWrangler is an **independent** project. It is not affiliated with, sponsored by, or endorsed by Meshtastic LLC, Apple Inc., Leaflet, the OpenStreetMap Foundation, Open-Meteo, or the Copernicus programme.

MeshWrangler's MIT license applies to MeshWrangler's independently authored code only. It does **not** relicense any upstream software, maps, databases, imagery, services, logos, or trademarks. Their respective licenses and service terms remain applicable.

## Meshtastic application and project

- Project: https://meshtastic.org/
- Apple application source: https://github.com/meshtastic/Meshtastic-Apple
- Apple application license: GPL-3.0; https://github.com/meshtastic/Meshtastic-Apple/blob/main/LICENSE
- Trademark rules: https://meshtastic.org/docs/legal/licensing-and-trademark/

Meshtastic® is a registered trademark of Meshtastic LLC. Meshtastic software components are released under various licenses, see GitHub for details. No warranty is provided - use at your own risk.

MeshWrangler reads user-supplied SQLite/SwiftData database snapshots produced by the Meshtastic application. The application is **not** included, altered, linked to, or redistributed here. Meshtastic protocol and application compatibility are not guarantees of official support.

## Independent extraction implementation and schema provenance

MeshWrangler's extraction utilities were independently developed to process historical database snapshots supplied by their owner. The database interpretation was derived by examining exported JSON records, querying the SQLite database and consulting publicly available Meshtastic Swift/application source documentation for field and relationship interpretation. This is a description of the project's development method, not a claim of official compatibility certification.

The distributed Python scripts use the standard-library `sqlite3` interface and do not import, link, embed, modify, or redistribute the Meshtastic Apple application's Swift code or binaries. Accessing stored application data and implementing an independently written reader does not, by itself, make the reader a derivative of the GPL-licensed application. Meshtastic's GPL-3.0 license continues to apply to Meshtastic's own software; MeshWrangler's MIT license covers only its independently authored code. Any future incorporation of upstream source code would require its own licensing review.

The inferred schema is an observed database format, not a documented stable API. Schema changes or differences between application versions can require new extraction logic; the supported behavior should be assessed against the actual files used. The utility does not circumvent Apple platform security controls or provide a method to bypass protections to obtain application data.

## Apple platforms

- Apple trademark and copyright guidelines: https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html

Apple, iOS, iPhone and macOS are referenced solely to identify the platforms and application-data sources involved. Apple software and trademark assets are not included. Apple Inc. does not sponsor or endorse MeshWrangler. Names and marks remain property of their respective owners.

## Leaflet

- JavaScript map engine: Leaflet 1.9.4, loaded at runtime from unpkg
- Website/source: https://leafletjs.com/ and https://github.com/Leaflet/Leaflet
- Code license: BSD-2-Clause; https://github.com/Leaflet/Leaflet/blob/v1.9.4/LICENSE
- CDN: https://unpkg.com/ (separate network service)

Leaflet is not distributed in the current source archive; its library and stylesheet are requested by the browser. Network access may be necessary for the Leaflet map. Leaflet's BSD-2-Clause license applies to Leaflet, not to MeshWrangler's original code.

## OpenStreetMap

- Map data: © OpenStreetMap contributors, under ODbL; https://www.openstreetmap.org/copyright
- Public raster tile service: https://tile.openstreetmap.org/
- Tile server policy: https://operations.osmfoundation.org/policies/tiles/

The current Explorer displays attribution on the tiled map. The public tile server is best-effort, is not a general offline map service, and **must not** be used to bulk-download, prefetch, or create offline map packages. Its tile policy also requires normal browser identification/`Referer` behavior and HTTP-compliant tile caching; browser privacy settings or opening a local `file://` page may affect these requests, so map availability is not guaranteed. The distribution does not bundle offline OSM tiles. A future regional/offline-map feature will require separately licensed and permitted map data or a suitable provider.

## Open-Meteo and Copernicus

- Hosted elevation endpoint: https://open-meteo.com/en/docs/elevation-api
- Open-Meteo API data license: CC BY 4.0; https://creativecommons.org/licenses/by/4.0/
- Open-Meteo current license and API-use terms: https://open-meteo.com/en/licence and https://open-meteo.com/en/terms
- Elevation source: Copernicus DEM 2021 GLO-90, approximately 90 m resolution
- Copernicus reference DOI: https://doi.org/10.5270/ESA-c5d3d65

Terrain elevations displayed by MeshWrangler are derived from Open-Meteo's elevation service using Copernicus DEM data. Credit: elevation data from **Open-Meteo and Copernicus**. The free hosted API is restricted to non-commercial use and published request limits; commercial deployment requires reviewing the provider's current terms, using an appropriate commercial plan, or selecting an authorized self-hosted alternative. Open-Meteo requires attribution to both Open-Meteo and Copernicus for elevation data. Elevation estimates are not survey-grade measurements.

## Data processing, network disclosures, and privacy

- The Python pipeline writes absolute source-folder paths into `exports/master_manifest.json` (`root`) and `exports/master_data/reconciliation_manifest.json` (`source_root`); generated manifests should not be published without reviewing/redacting these fields.
- User-selected node records are processed in the browser locally; the current Explorer does not intentionally upload complete NodeDB datasets to MeshWrangler servers.
- When enabled, terrain enrichment sends batches of latitude/longitude coordinates to `api.open-meteo.com` and caches terrain results in browser IndexedDB when permitted.
- Online basemap rendering requests map tiles from `tile.openstreetmap.org`; requests disclose viewed map areas and normal browser connection metadata to the provider.
- Leaflet resources are requested from `unpkg.com` and may disclose normal request metadata.
- Neither third-party service availability nor confidentiality of third-party requests is guaranteed. Consult the relevant providers' privacy policies.
- The existing coordinate-only offline fallback is not a full offline basemap. Regional offline map/terrain packages are planned, not implemented.

## Python

The four distributed Python utilities use Python standard-library modules for their core operations. The release supports CSV and JSON outputs; it does not provide XLSX export or require `artifact_tool`.

## Scope of these notices

References to external sources are acknowledgements and compatibility information, **not** claims of ownership, rights transfer, sublicense, or endorsement. Consult each linked upstream license and usage policy for the authoritative terms. These notices should be reviewed whenever online dependencies or data providers change.
