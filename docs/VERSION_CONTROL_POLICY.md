# MeshWrangler component predecessor policy (mandatory)

Before delivering ANY new candidate, package, push, or release:

1. Identify the immediately prior **accepted** ZIP, preserve it unchanged, and pin its filename and SHA-256 under `predecessor_checkpoint` in `COMPONENT_VERSIONS.json`.
2. Set `predecessor_version`, `predecessor_sha256`, and `changed_from_predecessor` for every source component using that exact ZIP; do not infer these fields from old release metadata.
3. Changed component bytes require a strictly higher internal component version; unchanged bytes require the same version. Any approved version-only exception must be separately documented and supported by an explicit checker exception; none currently exist.
4. HTML title, heading, internal marker; Python internal marker for changed Python sources; component manifest, hashes, and distribution checksums must agree.
5. Run `python3 tests/check_distribution.py NEW.zip IMMEDIATELY_PREVIOUS_ACCEPTED.zip [V1_BASELINE.zip]`. Any failure blocks delivery and publication. Test must reject a wrong predecessor ZIP, source drift with stale component version, and version bumps with unchanged source.
6. Retain the previous accepted ZIP, new ZIP, manifest and change record in the Library. A failed or merely built candidate does not become the accepted predecessor until accepted.

Project release tag `v1.1.0` identifies the assembled distribution, NOT every component version. Stable filenames are kept. Immutable published v1.0.0 baseline is not edited.
