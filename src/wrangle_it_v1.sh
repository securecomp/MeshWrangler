#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v python3 >/dev/null 2>&1 || { echo 'ERROR: python3 not found' >&2; exit 2; }
[[ -f backup-index.json ]] || { echo 'ERROR: backup-index.json not found in script directory' >&2; exit 2; }
for script in meshtastic_master_export_v1.py meshtastic_snapshot_export_v2.py meshtastic_consolidate_v2.py meshtastic_quality_flags_review_v1.py; do
  [[ -f "$script" ]] || { echo "ERROR: missing $script" >&2; exit 2; }
done
mkdir -p logs
log="logs/wrangle_it_$(date +%Y%m%d_%H%M%S)_$$.log"
exec > >(tee -a "$log") 2>&1
printf 'MeshWrangler started: %s\nLog: %s\n' "$(date)" "$PWD/$log"
stage=0
for script in meshtastic_master_export_v1.py meshtastic_consolidate_v2.py meshtastic_quality_flags_review_v1.py; do
  stage=$((stage + 1))
  echo "[START] Stage $stage: $script"
  if python3 "$script"; then
    echo "[PASS]  Stage $stage: $script"
  else
    rc=$?
    echo "[FAIL]  Stage $stage: $script (exit $rc); later stages skipped" >&2
    exit "$rc"
  fi
done
echo '[DONE] All three stages completed successfully.'
