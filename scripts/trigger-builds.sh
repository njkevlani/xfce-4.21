#!/usr/bin/env bash
# trigger-builds.sh - Trigger sequential builds for xfdesktop and companion packages using copr-cli
set -euo pipefail

PROJECT_NAME="${1:-xfce-4.21}"
BUILD_ORDER=("libxfce4util" "libxfce4windowing" "libxfce4ui" "xfce4-session" "xfdesktop")

echo "=========================================================="
echo " Triggering Sequential Copr Builds for: ${PROJECT_NAME}"
echo "=========================================================="

LAST_BUILD_ID=""

for pkg in "${BUILD_ORDER[@]}"; do
    echo "==> Submitting build for: ${pkg}..."
    if [ -z "${LAST_BUILD_ID}" ]; then
        OUTPUT="$(copr-cli build-package "${PROJECT_NAME}" --name "${pkg}" --nowait)"
    else
        echo "    (Configured to start after Build #${LAST_BUILD_ID})"
        OUTPUT="$(copr-cli build-package "${PROJECT_NAME}" --name "${pkg}" --nowait --after-build-id "${LAST_BUILD_ID}")"
    fi
    echo "    ${OUTPUT}"
    # Extract build ID from output (typically: "Created build: 1234567")
    BUILD_ID="$(echo "${OUTPUT}" | grep -oE '[0-9]+' | head -n 1 || true)"
    if [ -n "${BUILD_ID}" ]; then
        LAST_BUILD_ID="${BUILD_ID}"
        echo "    Build ID: ${BUILD_ID}"
    fi
done

echo ""
echo "All builds scheduled successfully!"
if [ -n "${LAST_BUILD_ID}" ]; then
    echo "To monitor the final xfdesktop build progress, run:"
    echo "  copr-cli watch-build ${LAST_BUILD_ID}"
fi
echo "Or check your Copr web dashboard."
