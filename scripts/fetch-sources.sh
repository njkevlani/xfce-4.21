#!/usr/bin/env bash
# fetch-sources.sh - Download upstream tarballs for xfdesktop and companion packages
set -euo pipefail

SOURCES_DIR="${1:-./sources}"
mkdir -p "${SOURCES_DIR}"

URLS=(
    "https://archive.xfce.org/src/xfce/xfdesktop/4.21/xfdesktop-4.21.1.tar.xz"
    "https://archive.xfce.org/src/xfce/libxfce4util/4.21/libxfce4util-4.21.0.tar.xz"
    "https://archive.xfce.org/src/xfce/libxfce4windowing/4.20/libxfce4windowing-4.20.7.tar.bz2"
    "https://archive.xfce.org/src/xfce/libxfce4ui/4.21/libxfce4ui-4.21.9.tar.xz"
    "https://archive.xfce.org/src/xfce/xfce4-session/4.21/xfce4-session-4.21.2.tar.xz"
)

echo "==> Downloading upstream Xfce source archives to ${SOURCES_DIR}..."
for url in "${URLS[@]}"; do
    filename="$(basename "${url}")"
    target="${SOURCES_DIR}/${filename}"
    if [ -f "${target}" ]; then
        echo "  [EXISTS] ${filename}"
    else
        echo "  [DOWNLOADING] ${url}..."
        curl -fSL "${url}" -o "${target}"
    fi
done

echo "==> All source archives downloaded successfully."
