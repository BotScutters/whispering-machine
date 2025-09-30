#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FW_DIR="$ROOT_DIR/firmware/wm_node"
NODES_INI="$FW_DIR/config/nodes.ini"

cd "$FW_DIR"

# Discover all OTA env names from nodes.ini: [env:nodeX-ota]
mapfile -t OTA_ENVS < <(grep -oE '^\[env:[^]]+-ota\]' "$NODES_INI" | sed -E 's/^\[env:|]$//')

if [[ ${#OTA_ENVS[@]} -eq 0 ]]; then
  echo "No *-ota environments found in $NODES_INI"
  exit 1
fi

echo "Found OTA envs:"
printf '  - %s\n' "${OTA_ENVS[@]}"
echo

# Optional: regenerate version header before build
if [[ -x "$ROOT_DIR/scripts/bump_version.sh" ]]; then
  "$ROOT_DIR/scripts/bump_version.sh"
fi

# Build once for each env (PlatformIO caches nicely) and upload
for ENV in "${OTA_ENVS[@]}"; do
  echo "==== Building & uploading for $ENV ===="
  pio run -e "$ENV" -t upload
  echo
done

echo "✅ Completed OTA uploads to: ${OTA_ENVS[*]}"
