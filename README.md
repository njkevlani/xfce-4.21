# Fedora Copr Build for Xfce Desktop Manager (xfdesktop 4.21)

This repository contains the Fedora RPM packaging specifications and CLI automation scripts to create, push, and maintain a [Fedora Copr](https://copr.fedorainfracloud.org) build repository for **xfdesktop 4.21** (the development series leading to Xfce 4.22) using the **GitHub CLI (`gh`)** and **Copr CLI (`copr-cli`)**.

---

## Table of Contents

- [Overview & Architecture](#overview--architecture)
  - [xfdesktop 4.21 Highlights](#xfdesktop-421-highlights)
  - [Dependency Chain & Companion Packages](#dependency-chain--companion-packages)
- [Repository Structure](#repository-structure)
- [Step-by-Step Setup using CLI (gh & copr-cli)](#step-by-step-setup-using-cli-gh--copr-cli)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Authenticate GitHub CLI (gh) & Copr CLI (copr-cli)](#2-authenticate-github-cli-gh--copr-cli)
  - [3. Create GitHub Repo and Push (One-Time via gh)](#3-create-github-repo-and-push-one-time-via-gh)
  - [4. Create Copr Project (via copr-cli)](#4-create-copr-project-via-copr-cli)
  - [5. Add Packages to Copr from GitHub (via copr-cli)](#5-add-packages-to-copr-from-github-via-copr-cli)
  - [6. Trigger Initial Builds in Dependency Order](#6-trigger-initial-builds-in-dependency-order)
  - [Optional: Automated All-in-One Setup Script](#optional-automated-all-in-one-setup-script)
- [How to Make Updates](#how-to-make-updates)
  - [1. Updating to a New Release](#1-updating-to-a-new-release)
  - [2. Triggering Rebuilds via copr-cli](#2-triggering-rebuilds-via-copr-cli)
  - [3. Automatic Webhook Rebuilds](#3-automatic-webhook-rebuilds)
- [How to Install for the End User](#how-to-install-for-the-end-user)
  - [1. Enable Copr Repository](#1-enable-copr-repository)
  - [2. Install or Upgrade xfdesktop](#2-install-or-upgrade-xfdesktop)
  - [3. Apply and Restart xfdesktop](#3-apply-and-restart-xfdesktop)
  - [4. Verify Version](#4-verify-version)
  - [5. Rollback / Revert](#5-rollback--revert)
- [Alternative: Copr Web UI Setup](#alternative-copr-web-ui-setup)
- [Local Building and Testing](#local-building-and-testing)

---

## Overview & Architecture

### xfdesktop 4.21 Highlights

The 4.21 development cycle modernizes `xfdesktop`:
- **Meson Build System**: Migrated completely from Autotools (`./configure && make`) to Meson and Ninja.
- **Native Wayland Support**: Deep integration with `gtk-layer-shell` and `libxfce4windowing` for Wayland desktop drawing.
- **Video Wallpaper Backdrops**: Support for video backdrops powered by GStreamer and `gst-plugin-gtk` (`gstreamer1-plugins-good-gtk`).
- **Modernized Session Integration**: Uses the new `libxfce4session-client` instead of deprecated `XfceSMClient`.

### Dependency Chain & Companion Packages

In Fedora official repositories (Fedora 41, 42, 43, 44), Xfce components are on the 4.20 stable series. However, `xfdesktop 4.21.x` requires newer development components:

```
xfdesktop 4.21.1
├── libxfce4session-client-1 >= 4.21.2  (provided by xfce4-session 4.21.2)
├── libxfce4ui-2 >= 4.21.0              (provided by libxfce4ui 4.21.9)
├── libxfce4windowing-0 >= 4.20.6       (provided by libxfce4windowing 4.20.7)
└── libxfce4util-1.0 >= 4.18.0          (provided by libxfce4util 4.21.0)
```

> [!IMPORTANT]
> Because standard Fedora repos do not yet provide `libxfce4session-client-1` and `libxfce4ui >= 4.21.0`, this Copr project builds these companion packages alongside `xfdesktop`. Copr automatically uses packages built inside the same project to satisfy dependencies for other builds.

---

## Repository Structure

```
.
├── xfdesktop.spec                     # Primary RPM spec file for xfdesktop 4.21.1
├── companion-specs/                   # Companion specs required for build dependencies
│   ├── libxfce4util.spec              # libxfce4util 4.21.0
│   ├── libxfce4windowing.spec         # libxfce4windowing 4.20.7
│   ├── libxfce4ui.spec                # libxfce4ui 4.21.9
│   └── xfce4-session.spec             # xfce4-session 4.21.2 (provides libxfce4session-client)
├── scripts/
│   ├── setup-copr.sh                  # All-in-one automation (gh repo create + copr-cli setup)
│   ├── trigger-builds.sh              # Sequential build trigger via copr-cli with --after-build-id
│   ├── fetch-sources.sh               # Download official upstream release tarballs
│   └── build-srpm.sh                  # Generate Source RPMs locally or via container
├── copr-cli.conf.example              # Configuration template for ~/.config/copr
└── README.md                          # Full guide and documentation
```

---

## Step-by-Step Setup using CLI (`gh` & `copr-cli`)

### 1. Prerequisites

Ensure `gh` and `copr-cli` are installed on your Fedora system:

```bash
sudo dnf install -y gh copr-cli git
```

---

### 2. Authenticate GitHub CLI (`gh`) & Copr CLI (`copr-cli`)

#### A. Log in to GitHub CLI:
```bash
gh auth login
```
- Select **GitHub.com** -> **HTTPS** -> Authenticate with your web browser or personal access token.
- Verify authentication:
  ```bash
  gh auth status
  ```

#### B. Configure Copr CLI:
1. Log in to [Fedora Copr](https://copr.fedorainfracloud.org/) with your Fedora Account System (FAS) credentials.
2. Open the [Copr API tokens page](https://copr.fedorainfracloud.org/api/).
3. Copy the configuration block and save it to `~/.config/copr`:
   ```bash
   mkdir -p ~/.config
   cat << 'EOF' > ~/.config/copr
   [copr-cli]
   login = <your-fas-username>
   username = <your-fas-username>
   token = <your-api-token>
   copr_url = https://copr.fedorainfracloud.org
   EOF
   chmod 600 ~/.config/copr
   ```
4. Verify Copr authentication:
   ```bash
   copr-cli whoami
   ```

---

### 3. Create GitHub Repo and Push (One-Time via `gh`)

Run the following command directly inside this project repository:

```bash
# 1. Create a public repository on GitHub and push the initial commit
gh repo create xfce-4.21 --public --source=. --remote=origin --push

# 2. Get the clone URL (HTTPS format required by Copr)
GH_USER="$(gh api user -q .login)"
REPO_URL="https://github.com/${GH_USER}/xfce-4.21"
echo "Repository created at: ${REPO_URL}"
```

---

### 4. Create Copr Project (via `copr-cli`)

Create the Copr project with the target Fedora chroots:

```bash
PROJECT_NAME="xfce-4.21"

copr-cli create "${PROJECT_NAME}" \
    --chroot fedora-rawhide-x86_64 \
    --chroot fedora-44-x86_64 \
    --chroot fedora-43-x86_64 \
    --chroot fedora-42-x86_64 \
    --description "Xfce 4.21 development series (xfdesktop 4.21 and core companion packages)" \
    --instructions "sudo dnf copr enable $(copr-cli whoami)/${PROJECT_NAME} && sudo dnf install xfdesktop" \
    --follow-fedora-branching on
```

*(You can also add aarch64 chroots if desired, e.g. `--chroot fedora-rawhide-aarch64`).*

---

### 5. Add Packages to Copr from GitHub (via `copr-cli`)

Register all packages as SCM packages in Copr pointing to your GitHub repository:

```bash
GH_USER="$(gh api user -q .login)"
REPO_URL="https://github.com/${GH_USER}/xfce-4.21"
PROJECT_NAME="xfce-4.21"

# 1. Base utility library
copr-cli add-package-scm "${PROJECT_NAME}" --name libxfce4util \
    --clone-url "${REPO_URL}" --commit main \
    --spec companion-specs/libxfce4util.spec --webhook-rebuild on

# 2. Windowing abstraction library
copr-cli add-package-scm "${PROJECT_NAME}" --name libxfce4windowing \
    --clone-url "${REPO_URL}" --commit main \
    --spec companion-specs/libxfce4windowing.spec --webhook-rebuild on

# 3. UI widget library
copr-cli add-package-scm "${PROJECT_NAME}" --name libxfce4ui \
    --clone-url "${REPO_URL}" --commit main \
    --spec companion-specs/libxfce4ui.spec --webhook-rebuild on

# 4. Session manager and libxfce4session-client
copr-cli add-package-scm "${PROJECT_NAME}" --name xfce4-session \
    --clone-url "${REPO_URL}" --commit main \
    --spec companion-specs/xfce4-session.spec --webhook-rebuild on

# 5. Desktop manager (xfdesktop 4.21)
copr-cli add-package-scm "${PROJECT_NAME}" --name xfdesktop \
    --clone-url "${REPO_URL}" --commit main \
    --spec xfdesktop.spec --webhook-rebuild on
```

---

### 6. Trigger Initial Builds in Dependency Order

Because `xfdesktop` depends on the companion libraries, submit the builds in order using `--after-build-id` so Copr automatically chains them:

```bash
PROJECT_NAME="xfce-4.21"

# Build 1: libxfce4util
B1=$(copr-cli build-package "${PROJECT_NAME}" --name libxfce4util --nowait | grep -oE '[0-9]+' | head -1)

# Build 2: libxfce4windowing (runs after libxfce4util)
B2=$(copr-cli build-package "${PROJECT_NAME}" --name libxfce4windowing --nowait --after-build-id "${B1}" | grep -oE '[0-9]+' | head -1)

# Build 3: libxfce4ui (runs after libxfce4windowing)
B3=$(copr-cli build-package "${PROJECT_NAME}" --name libxfce4ui --nowait --after-build-id "${B2}" | grep -oE '[0-9]+' | head -1)

# Build 4: xfce4-session (runs after libxfce4ui)
B4=$(copr-cli build-package "${PROJECT_NAME}" --name xfce4-session --nowait --after-build-id "${B3}" | grep -oE '[0-9]+' | head -1)

# Build 5: xfdesktop (runs after xfce4-session)
B5=$(copr-cli build-package "${PROJECT_NAME}" --name xfdesktop --nowait --after-build-id "${B4}" | grep -oE '[0-9]+' | head -1)

echo "All builds scheduled! Final build ID (xfdesktop): ${B5}"
```

To watch the progress of the final build:
```bash
copr-cli watch-build "${B5}"
```

---

### Optional: Automated All-in-One Setup Script

Instead of running steps 3–6 manually, you can run the included helper scripts:

```bash
# Creates the GitHub repo, creates Copr project, and configures all packages:
./scripts/setup-copr.sh xfce-4.21

# Triggers the sequential chained build on Copr:
./scripts/trigger-builds.sh xfce-4.21
```

---

## How to Make Updates

### 1. Updating to a New Release

When upstream releases a new development snapshot (e.g., `xfdesktop 4.21.2`):

1. **Update `xfdesktop.spec`**:
   ```spec
   Version:        4.21.2
   ```
2. **Commit and push using Git**:
   ```bash
   git add xfdesktop.spec
   git commit -m "Update xfdesktop to 4.21.2"
   git push origin main
   ```

### 2. Triggering Rebuilds via `copr-cli`

Trigger a build for any package immediately:

```bash
# Rebuild xfdesktop:
copr-cli build-package xfce-4.21 --name xfdesktop

# Monitor status:
copr-cli monitor xfce-4.21
```

To rebuild only for a specific distribution chroot (e.g., Rawhide):
```bash
copr-cli build-package xfce-4.21 --name xfdesktop -r fedora-rawhide-x86_64
```

### 3. Automatic Webhook Rebuilds

Because packages were added with `--webhook-rebuild on`, you can link GitHub pushes to Copr:

1. Obtain your package webhook secret:
   ```bash
   copr-cli new-webhook-secret xfce-4.21
   ```
2. In your GitHub repository:
   - Go to **Settings** -> **Webhooks** -> **Add webhook**.
   - **Payload URL**: `https://copr.fedorainfracloud.org/webhooks/custom/<user>/xfce-4.21/<pkgname>/`
   - **Content type**: `application/json`
   - **Secret**: Your Copr webhook secret.
3. Every commit pushed to `main` will automatically trigger a Copr rebuild!

---

## How to Install for the End User

### 1. Enable Copr Repository

Ensure `dnf-plugins-core` is present, then enable the repository:

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf copr enable <username>/xfce-4.21
```

### 2. Install or Upgrade xfdesktop

- **Fresh installation**:
  ```bash
  sudo dnf install xfdesktop
  ```

- **Upgrading an existing Xfce desktop**:
  ```bash
  sudo dnf upgrade --refresh xfdesktop
  ```

*(To upgrade the complete 4.21 test stack)*:
```bash
sudo dnf upgrade --refresh libxfce4util libxfce4windowing libxfce4ui xfce4-session xfdesktop
```

### 3. Apply and Restart xfdesktop

You do not need to reboot your machine:

```bash
# Reload wallpapers and icon settings:
xfdesktop --reload

# Or replace the active instance cleanly:
xfdesktop --replace &
```

*(If running on Wayland compositor like Labwc or Wayfire, restart the compositor or log out and log back in).*

### 4. Verify Version

Confirm the new development version is active:

```bash
xfdesktop --version
```
Expected output:
```
xfdesktop 4.21.1 (Xfce 4.21)
```

Launch the updated settings dialog:
```bash
xfdesktop-settings
```

### 5. Rollback / Revert

To revert back to official Fedora packages:

```bash
# Disable the Copr repository
sudo dnf copr disable <username>/xfce-4.21

# Downgrade packages back to Fedora official repository versions
sudo dnf distro-sync
```

---

## Alternative: Copr Web UI Setup

If you prefer using the web browser interface instead of `copr-cli`:

1. Visit [Fedora Copr](https://copr.fedorainfracloud.org/) and click **New Project**.
2. Name the project `xfce-4.21` and select your target Fedora chroots.
3. Under **Packages** -> **New Package**, select **SCM**:
   - **Clone URL**: `https://github.com/<your-username>/xfce-4.21`
   - **Committish**: `main`
   - **Spec file path**: `xfdesktop.spec` (and companion paths for the other packages)
4. Build in the dependency order: `libxfce4util` -> `libxfce4windowing` -> `libxfce4ui` -> `xfce4-session` -> `xfdesktop`.

---

## Local Building and Testing

If you wish to test building the RPMs locally before pushing to Copr:

1. **Download source tarballs**:
   ```bash
   ./scripts/fetch-sources.sh
   ```

2. **Generate Source RPMs (SRPMs)**:
   ```bash
   ./scripts/build-srpm.sh
   ```

3. **Build in local Mock chroot** (optional):
   ```bash
   sudo dnf install -y mock
   mock -r fedora-rawhide-x86_64 --rebuild srpms/xfdesktop-4.21.1-*.src.rpm
   ```
