# Fedora Copr Build for Xfce Desktop Manager (xfdesktop 4.21)

This repository contains the Fedora RPM packaging specifications and instructions to create, automate, and maintain a [Fedora Copr](https://copr.fedorainfracloud.org) build repository for **xfdesktop 4.21** (the development series leading to Xfce 4.22).

---

## Table of Contents

- [Overview & Architecture](#overview--architecture)
  - [xfdesktop 4.21 Highlights](#xfdesktop-421-highlights)
  - [Dependency Chain](#dependency-chain)
- [Repository Structure](#repository-structure)
- [How to Set Up on Fedora Copr](#how-to-set-up-on-fedora-copr)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Create the Copr Project](#2-create-the-copr-project)
  - [3. Add the Packages (Method A: SCM / Git Webhook - Recommended)](#3-add-the-packages-method-a-scm--git-webhook---recommended)
  - [4. Add the Packages (Method B: Command Line with copr-cli)](#4-add-the-packages-method-b-command-line-with-copr-cli)
  - [5. Initial Build Order](#5-initial-build-order)
- [How to Make Updates](#how-to-make-updates)
  - [Updating to a New Upstream Release](#updating-to-a-new-upstream-release)
  - [Triggering Rebuilds](#triggering-rebuilds)
- [How to Install for the End User](#how-to-install-for-the-end-user)
  - [1. Enable the Copr Repository](#1-enable-the-copr-repository)
  - [2. Install or Upgrade xfdesktop](#2-install-or-upgrade-xfdesktop)
  - [3. Apply and Restart xfdesktop](#3-apply-and-restart-xfdesktop)
  - [4. Verify Installation](#4-verify-installation)
  - [5. Rollback / Uninstall](#5-rollback--uninstall)
- [Local Building and Testing](#local-building-and-testing)

---

## Overview & Architecture

### xfdesktop 4.21 Highlights

The 4.21 development cycle brings major architectural advancements to `xfdesktop`:
- **Meson Build System**: Migrated completely from Autotools (`./configure && make`) to Meson and Ninja.
- **Native Wayland Support**: Deep integration with `gtk-layer-shell` and `libxfce4windowing` for Wayland desktop drawing.
- **Video Wallpaper Backdrops**: Support for video backdrops powered by GStreamer and `gst-plugin-gtk` (`gstreamer1-plugins-good-gtk`).
- **Modernized Session Integration**: Uses the new `libxfce4session-client` instead of deprecated `XfceSMClient`.

### Dependency Chain

In Fedora official repositories (Fedora 41, 42, 43, 44), Xfce components are on the 4.20 stable series. However, `xfdesktop 4.21.x` requires newer development components:

```
xfdesktop 4.21.1
├── libxfce4session-client-1 >= 4.21.2  (provided by xfce4-session 4.21.2)
├── libxfce4ui-2 >= 4.21.0              (provided by libxfce4ui 4.21.9)
├── libxfce4windowing-0 >= 4.20.6       (provided by libxfce4windowing 4.20.7)
└── libxfce4util-1.0 >= 4.18.0          (provided by libxfce4util 4.21.0)
```

> [!IMPORTANT]
> Because standard Fedora repos do not yet provide `libxfce4session-client-1` and `libxfce4ui >= 4.21.0`, your Copr project should host these companion packages alongside `xfdesktop`. Copr automatically uses packages built inside the same project to satisfy dependencies for other builds.

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
│   ├── fetch-sources.sh               # Download official upstream release tarballs
│   └── build-srpm.sh                  # Generate Source RPMs locally or via container
├── copr-cli.conf.example              # Configuration template for ~/.config/copr
└── README.md                          # Full guide and documentation
```

---

## How to Set Up on Fedora Copr

### 1. Prerequisites

1. Create a [Fedora Account (FAS)](https://accounts.fedoraproject.org/) if you don't already have one.
2. Sign in to [Fedora Copr](https://copr.fedorainfracloud.org/).
3. Push this repository to GitHub, GitLab, or Pagure (e.g. `https://github.com/<your-username>/xfce-4.21`).

---

### 2. Create the Copr Project

1. On https://copr.fedorainfracloud.org, click **New Project** in the navigation bar.
2. Fill in the project details:
   - **Project Name**: `xfce-4.21` (or `xfdesktop-4.21`)
   - **Description**: `Development builds of xfdesktop 4.21 and Xfce 4.21 core components for Fedora.`
   - **Instructions**:
     ```
     sudo dnf copr enable <your-username>/xfce-4.21
     sudo dnf install xfdesktop
     ```
3. Select your target **Chroots** (architectures and releases):
   - `fedora-rawhide-x86_64`
   - `fedora-rawhide-aarch64`
   - `fedora-44-x86_64` / `fedora-44-aarch64`
   - `fedora-43-x86_64` / `fedora-43-aarch64`
   - `fedora-42-x86_64` / `fedora-42-aarch64`
4. Under **Settings**:
   - Check **Follow Fedora branching** (retains your builds when Fedora versions branch).
   - Check **Auto-prune old builds** (recommended to save disk space).
5. Click **Save**.

---

### 3. Add the Packages (Method A: SCM / Git Webhook - Recommended)

Using the SCM method allows Copr to build directly from your Git repository whenever you push changes.

#### Adding Companion Packages:

Navigate to **Packages** -> **New Package** for each package:

| Package Name | Clone URL | Committish | Spec file path |
| :--- | :--- | :--- | :--- |
| `libxfce4util` | `https://github.com/<user>/xfce-4.21` | `main` | `companion-specs/libxfce4util.spec` |
| `libxfce4windowing` | `https://github.com/<user>/xfce-4.21` | `main` | `companion-specs/libxfce4windowing.spec` |
| `libxfce4ui` | `https://github.com/<user>/xfce-4.21` | `main` | `companion-specs/libxfce4ui.spec` |
| `xfce4-session` | `https://github.com/<user>/xfce-4.21` | `main` | `companion-specs/xfce4-session.spec` |

#### Adding `xfdesktop`:

1. Click **New Package**.
2. **Package Name**: `xfdesktop`
3. Under **Source Type**, choose **SCM**.
4. Set:
   - **Clone URL**: `https://github.com/<user>/xfce-4.21`
   - **Committish**: `main`
   - **Spec file path**: `xfdesktop.spec`
5. Click **Create**.

#### Enabling Automated Webhooks:
1. In Copr, go to the package's **Integrations** tab.
2. Copy the **Webhook URL**.
3. In your GitHub repository, go to **Settings** -> **Webhooks** -> **Add webhook**, paste the URL, select `application/json`, and trigger on **Push events**.
4. Now, every `git push` to your repository automatically triggers a build on Copr!

---

### 4. Add the Packages (Method B: Command Line with `copr-cli`)

If you prefer using the command line:

1. Install `copr-cli`:
   ```bash
   sudo dnf install copr-cli
   ```
2. Configure API credentials:
   - Obtain your API token from: https://copr.fedorainfracloud.org/api/
   - Save it to `~/.config/copr`:
     ```ini
     [copr-cli]
     login = <your-username>
     username = <your-username>
     token = <your-api-token>
     copr_url = https://copr.fedorainfracloud.org
     ```
3. Create the project:
   ```bash
   copr-cli create xfce-4.21 \
       --chroot fedora-rawhide-x86_64 \
       --chroot fedora-44-x86_64 \
       --chroot fedora-43-x86_64 \
       --description "Xfce 4.21 development packages and xfdesktop 4.21"
   ```
4. Add the packages from Git:
   ```bash
   REPO_URL="https://github.com/<user>/xfce-4.21"

   copr-cli add-package-scm xfce-4.21 --name libxfce4util \
       --clone-url "${REPO_URL}" --commit main --spec companion-specs/libxfce4util.spec

   copr-cli add-package-scm xfce-4.21 --name libxfce4windowing \
       --clone-url "${REPO_URL}" --commit main --spec companion-specs/libxfce4windowing.spec

   copr-cli add-package-scm xfce-4.21 --name libxfce4ui \
       --clone-url "${REPO_URL}" --commit main --spec companion-specs/libxfce4ui.spec

   copr-cli add-package-scm xfce-4.21 --name xfce4-session \
       --clone-url "${REPO_URL}" --commit main --spec companion-specs/xfce4-session.spec

   copr-cli add-package-scm xfce-4.21 --name xfdesktop \
       --clone-url "${REPO_URL}" --commit main --spec xfdesktop.spec
   ```

---

### 5. Initial Build Order

Because `xfdesktop` depends on the companion libraries, run the initial builds in order so the chroots have the required RPMs available:

```bash
# Step 1: Base utilities
copr-cli build-package xfce-4.21 --name libxfce4util
# (Wait for completion)

# Step 2: Windowing abstraction
copr-cli build-package xfce-4.21 --name libxfce4windowing
# (Wait for completion)

# Step 3: UI widgets
copr-cli build-package xfce-4.21 --name libxfce4ui
# (Wait for completion)

# Step 4: Session manager & client library
copr-cli build-package xfce-4.21 --name xfce4-session
# (Wait for completion)

# Step 5: Desktop manager
copr-cli build-package xfce-4.21 --name xfdesktop
```

*Note: In the Copr Web UI, you can trigger these sequentially by clicking **Build** on each package page.*

---

## How to Make Updates

### Updating to a New Upstream Release

When a new development release arrives (e.g. `xfdesktop-4.21.2`):

1. **Edit `xfdesktop.spec`**:
   ```spec
   Version:        4.21.2
   ```
2. **If dependencies changed**, update the `BuildRequires:` or `meson` flags accordingly.
3. **Commit and Push**:
   ```bash
   git add xfdesktop.spec
   git commit -m "Update xfdesktop to 4.21.2"
   git push origin main
   ```

### Triggering Rebuilds

- **Automatic (Webhook)**: If webhooks are configured, your `git push` will start the build automatically.
- **Web UI**: Go to `https://copr.fedorainfracloud.org/coprs/<user>/xfce-4.21/package/xfdesktop/` and click **Rebuild**.
- **CLI**:
  ```bash
  copr-cli build-package xfce-4.21 --name xfdesktop
  ```

---

## How to Install for the End User

### 1. Enable the Copr Repository

Ensure `dnf-plugins-core` is installed, then enable your repository:

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf copr enable <username>/xfce-4.21
```

Confirm when prompted to trust the repository key.

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

You do not need to reboot. To reload or replace the running desktop manager:

```bash
# Reload wallpaper and settings
xfdesktop --reload

# Or replace the active running instance
xfdesktop --replace &
```

*(If running Wayland compositor such as Labwc or Wayfire, restart the compositor or log out and log back in).*

### 4. Verify Installation

Check that the new version is active:

```bash
xfdesktop --version
```
Expected output:
```
xfdesktop 4.21.1 (Xfce 4.21)
```

Launch settings to test video wallpapers or icons:
```bash
xfdesktop-settings
```

### 5. Rollback / Uninstall

If the user wants to revert back to standard Fedora packages:

```bash
# Disable the Copr repository
sudo dnf copr disable <username>/xfce-4.21

# Revert installed packages to Fedora official repository versions
sudo dnf distro-sync
```

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
