#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FW_DIR="$ROOT_DIR/firmware/wm_node"
HDR="$FW_DIR/src/wm_version.h"

cd "$ROOT_DIR"

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo 'nogit')"
DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

cat > "$HDR" <<EOF
#pragma once
#define WM_GIT_SHA "${SHA}"
#define WM_BUILD_UTC "${DATE}"
EOF

echo "Generated $HDR  (SHA=${SHA}, DATE=${DATE})"
