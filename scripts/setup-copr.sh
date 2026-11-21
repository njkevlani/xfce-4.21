#!/usr/bin/env bash
# setup-copr.sh - Automate GitHub repo creation (via gh cli) and Copr configuration (via copr-cli)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_DIR}"

PROJECT_NAME="${1:-xfce-4.21}"

echo "=========================================================="
echo " Fedora Copr Setup for xfdesktop 4.21 (via gh & copr-cli)"
echo "=========================================================="

# 1. Verify Prerequisites
if ! command -v gh >/dev/null 2>&1; then
    echo "Error: gh (GitHub CLI) is not installed. Install with: sudo dnf install gh" >&2
    exit 1
fi

if ! command -v copr-cli >/dev/null 2>&1; then
    echo "Error: copr-cli is not installed. Install with: sudo dnf install copr-cli" >&2
    exit 1
fi

# 2. Check GitHub CLI Authentication
echo "==> Checking GitHub CLI authentication..."
if ! gh auth status >/dev/null 2>&1; then
    echo "You are not logged into GitHub. Launching login..."
    gh auth login -w -s repo
fi
GH_USER="$(gh api user -q .login 2>/dev/null || gh auth status 2>&1 | grep -o 'account [^ ]*' | awk '{print $2}' | head -n 1)"
echo "    Logged in to GitHub as: ${GH_USER}"

# 3. Check Copr CLI Configuration
echo "==> Checking Copr CLI configuration..."
if [ ! -f "${HOME}/.config/copr" ]; then
    echo "Error: ~/.config/copr configuration file not found!" >&2
    echo "Please generate an API token at https://copr.fedorainfracloud.org/api/" >&2
    echo "and save it to ~/.config/copr (see copr-cli.conf.example)." >&2
    exit 1
fi

COPR_USER="$(copr-cli whoami 2>/dev/null || true)"
if [ -z "${COPR_USER}" ]; then
    echo "Error: copr-cli authentication failed. Please verify ~/.config/copr" >&2
    exit 1
fi
echo "    Logged in to Copr as: ${COPR_USER}"

# 4. Create GitHub Repository and Push (One-time)
echo "==> Creating GitHub repository '${PROJECT_NAME}' and pushing code..."
if git remote get-url origin >/dev/null 2>&1; then
    CLONE_URL="$(git remote get-url origin)"
    echo "    Git remote 'origin' already exists: ${CLONE_URL}"
    echo "    Pushing latest commits..."
    git push -u origin main
else
    gh repo create "${PROJECT_NAME}" --public --source=. --remote=origin --push
    CLONE_URL="https://github.com/${GH_USER}/${PROJECT_NAME}"
    echo "    Created GitHub repo: ${CLONE_URL}"
fi

# Ensure URL is https format for Copr
if [[ "${CLONE_URL}" =~ ^git@github\.com:(.+)\.git$ ]]; then
    CLONE_URL="https://github.com/${BASH_REMATCH[1]}"
elif [[ "${CLONE_URL}" =~ \.git$ ]]; then
    CLONE_URL="${CLONE_URL%.git}"
fi

# 5. Create Copr Project
echo "==> Creating Copr project '${PROJECT_NAME}'..."
if copr-cli get "${PROJECT_NAME}" >/dev/null 2>&1; then
    echo "    Copr project '${PROJECT_NAME}' already exists."
else
    copr-cli create "${PROJECT_NAME}" \
        --chroot fedora-rawhide-x86_64 \
        --chroot fedora-44-x86_64 \
        --chroot fedora-43-x86_64 \
        --description "Xfce 4.21 development series (xfdesktop 4.21 and core companion packages)" \
        --instructions "sudo dnf copr enable ${COPR_USER}/${PROJECT_NAME} && sudo dnf install xfdesktop" \
        --follow-fedora-branching on
    echo "    Created Copr project '${PROJECT_NAME}'."
fi

# 6. Register Packages in Copr
echo "==> Registering SCM packages in Copr..."

declare -A PACKAGES=(
    ["libxfce4util"]="companion-specs/libxfce4util.spec"
    ["libxfce4windowing"]="companion-specs/libxfce4windowing.spec"
    ["libxfce4ui"]="companion-specs/libxfce4ui.spec"
    ["xfce4-session"]="companion-specs/xfce4-session.spec"
    ["xfdesktop"]="xfdesktop.spec"
)

for pkg in "libxfce4util" "libxfce4windowing" "libxfce4ui" "xfce4-session" "xfdesktop"; do
    spec_path="${PACKAGES[$pkg]}"
    echo "    Adding package '${pkg}' (spec: ${spec_path})..."
    copr-cli add-package-scm "${PROJECT_NAME}" \
        --name "${pkg}" \
        --clone-url "${CLONE_URL}" \
        --commit main \
        --spec "${spec_path}" \
        --webhook-rebuild on 2>/dev/null || \
    copr-cli edit-package-scm "${PROJECT_NAME}" \
        --name "${pkg}" \
        --clone-url "${CLONE_URL}" \
        --commit main \
        --spec "${spec_path}" \
        --webhook-rebuild on
done

echo ""
echo "=========================================================="
echo " Setup complete!"
echo " Project URL: https://copr.fedorainfracloud.org/coprs/${COPR_USER}/${PROJECT_NAME}/"
echo " GitHub URL:  ${CLONE_URL}"
echo "=========================================================="
echo ""
echo "To trigger the sequential initial builds in Copr, run:"
echo "  ./scripts/trigger-builds.sh ${PROJECT_NAME}"
