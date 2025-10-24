#!/bin/bash
# Generate wm_version.h with git information and build details

VERSION_FILE="firmware/wm_node/src/wm_version.h"
VERSION="1.0.0"

# Get git information
if git rev-parse --git-dir > /dev/null 2>&1; then
    GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
else
    GIT_SHA="unknown"
    GIT_BRANCH="unknown"
fi

# Get build timestamp
BUILD_UTC=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
BUILD_DATE=$(date +"%b %d %Y")
BUILD_TIME=$(date +"%H:%M:%S")

# Generate the version file
cat > "$VERSION_FILE" << EOF
#pragma once

// Version information
#define WM_VERSION "$VERSION"
#define WM_GIT_SHA "$GIT_SHA"
#define WM_GIT_BRANCH "$GIT_BRANCH"

// Build information
#define WM_BUILD_DATE "$BUILD_DATE"
#define WM_BUILD_TIME "$BUILD_TIME"
#define WM_BUILD_UTC "$BUILD_UTC"

// Compile-time macros
#define WM_BUILD_TIMESTAMP __DATE__ " " __TIME__
EOF

echo "Generated $VERSION_FILE with:"
echo "  Version: $VERSION"
echo "  Git SHA: $GIT_SHA"
echo "  Git Branch: $GIT_BRANCH"
echo "  Build UTC: $BUILD_UTC"
