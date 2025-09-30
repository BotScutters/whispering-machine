#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <node_id> [serial_port]"
  echo "Example: $0 node1 /dev/cu.usbserial-0001"
  exit 1
fi

NODE_ID="$1"        # e.g., node1
SERIAL_PORT="${2:-}" # optional

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FW_DIR="$ROOT_DIR/firmware/wm_node"

ENV_NAME="${NODE_ID}-usb"   # expects [env:node1-usb] in nodes.ini

cd "$FW_DIR"

# Optional: regenerate version header before build
if [[ -x "$ROOT_DIR/scripts/bump_version.sh" ]]; then
  "$ROOT_DIR/scripts/bump_version.sh"
fi

if [[ -n "$SERIAL_PORT" ]]; then
  echo "Flashing $ENV_NAME via $SERIAL_PORT"
  pio run -e "$ENV_NAME" -t upload --upload-port "$SERIAL_PORT"
else
  echo "Flashing $ENV_NAME (PlatformIO will auto-detect serial)"
  pio run -e "$ENV_NAME" -t upload
fi

echo "✅ USB flash done for $ENV_NAME"
