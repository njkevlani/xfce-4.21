#!/usr/bin/env bash
# build-srpm.sh - Generate Source RPMs (SRPMs) for xfdesktop and companion packages
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${1:-${REPO_ROOT}/srpms}"
SOURCES_DIR="${REPO_ROOT}/sources"

mkdir -p "${OUTPUT_DIR}" "${SOURCES_DIR}"

# Download sources first
"${REPO_ROOT}/scripts/fetch-sources.sh" "${SOURCES_DIR}"

build_srpm() {
    local spec_file="$1"
    echo "==> Building SRPM for ${spec_file}..."

    if command -v rpmbuild >/dev/null 2>&1; then
        rpmbuild -bs \
            --define "_topdir ${REPO_ROOT}/.rpmbuild" \
            --define "_sourcedir ${SOURCES_DIR}" \
            --define "_srcrpmdir ${OUTPUT_DIR}" \
            "${spec_file}"
    elif command -v podman >/dev/null 2>&1 || command -v docker >/dev/null 2>&1; then
        local engine="podman"
        command -v podman >/dev/null 2>&1 || engine="docker"
        echo "rpmbuild not found locally; building via ${engine} container (fedora:rawhide)..."
        ${engine} run --rm \
            -v "${REPO_ROOT}:/work:z" \
            -w /work \
            fedora:rawhide \
            bash -c "dnf install -y rpm-build rpmdevtools && \
                     rpmbuild -bs --define '_topdir /work/.rpmbuild' \
                                  --define '_sourcedir /work/sources' \
                                  --define '_srcrpmdir /work/srpms' \
                                  '/work/${spec_file#${REPO_ROOT}/}'"
    else
        echo "Error: Neither rpmbuild nor podman/docker found on system." >&2
        echo "Install rpm-build locally with: sudo dnf install rpm-build rpmdevtools" >&2
        exit 1
    fi
}

# Build companion SRPMs
for spec in "${REPO_ROOT}"/companion-specs/*.spec; do
    [ -f "${spec}" ] && build_srpm "${spec}"
done

# Build xfdesktop SRPM
build_srpm "${REPO_ROOT}/xfdesktop.spec"

echo ""
echo "==> Finished! SRPMs generated in: ${OUTPUT_DIR}"
ls -lh "${OUTPUT_DIR}"/*.src.rpm 2>/dev/null || true
