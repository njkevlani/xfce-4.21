%global xfceversion 4.21

Name:           xfdesktop
Version:        4.21.1
Release:        %autorelease
Summary:        Desktop manager for the Xfce Desktop Environment

License:        GPL-2.0-or-later
URL:            https://docs.xfce.org/xfce/xfdesktop/start
Source0:        https://archive.xfce.org/src/xfce/%{name}/%{xfceversion}/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson >= 0.56.0
BuildRequires:  ninja-build
BuildRequires:  gettext
BuildRequires:  desktop-file-utils

# Core Xfce & GTK libraries
BuildRequires:  pkgconfig(glib-2.0) >= 2.72.0
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.72.0
BuildRequires:  pkgconfig(gtk+-3.0) >= 3.24.0
BuildRequires:  pkgconfig(libxfce4util-1.0) >= 4.18.0
BuildRequires:  pkgconfig(libxfce4ui-2) >= 4.21.0
BuildRequires:  pkgconfig(libxfce4kbd-private-3)
BuildRequires:  pkgconfig(libxfce4windowing-0) >= 4.20.6
BuildRequires:  pkgconfig(libxfce4windowingui-0) >= 4.20.6
BuildRequires:  pkgconfig(libxfce4session-client-1) >= 4.21.2
BuildRequires:  pkgconfig(libxfconf-0) >= 4.19.3

# Desktop Menu, Thunar Extensions, File Icons, Notifications
BuildRequires:  pkgconfig(garcon-1) >= 4.18.0
BuildRequires:  pkgconfig(garcon-gtk3-1) >= 4.18.0
BuildRequires:  pkgconfig(thunarx-3) >= 4.18.0
BuildRequires:  pkgconfig(libnotify) >= 0.4.0
BuildRequires:  pkgconfig(yaml-0.1) >= 0.2.5

# Display Server Backends: X11 & Wayland
BuildRequires:  pkgconfig(x11) >= 1.6.7
BuildRequires:  pkgconfig(gdk-x11-3.0) >= 3.24.0
BuildRequires:  pkgconfig(libxfce4windowing-x11-0) >= 4.20.6
BuildRequires:  pkgconfig(gdk-wayland-3.0) >= 3.24.0
BuildRequires:  pkgconfig(gtk-layer-shell-0) >= 0.7.0
BuildRequires:  libSM-devel
BuildRequires:  libICE-devel

# Feature: Video Backdrop support
BuildRequires:  pkgconfig(gstreamer-1.0) >= 1.18.0
BuildRequires:  gstreamer1-plugins-good-gtk

# Runtime requirements
Requires:       libxfce4ui%{?_isa} >= 4.21.0
Requires:       libxfce4windowing%{?_isa} >= 4.20.6
Requires:       libxfce4util%{?_isa} >= 4.21.0
Requires:       xfwm4 >= 4.20.0
Requires:       xfce4-panel >= 4.20.0
Requires:       redhat-menus
Requires:       desktop-backgrounds-compat

%description
This package provides the desktop manager for the Xfce Desktop Environment.
It manages desktop background wallpapers (including video backdrops),
desktop icons, window navigation lists, and the desktop context menu.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%meson \
    -Ddefault-backdrop-filename=%{_datadir}/backgrounds/images/default.jxl \
    -Dvideo-backdrop=true \
    -Ddesktop-menu=enabled \
    -Ddesktop-icons=true \
    -Dfile-icons=true \
    -Dthunarx=enabled \
    -Dnotifications=enabled \
    -Dx11=enabled \
    -Dwayland=enabled \
    -Dtests=false
%meson_build

%install
%meson_install

# Validate desktop entry files
desktop-file-validate %{buildroot}%{_datadir}/applications/xfdesktop-settings.desktop
desktop-file-validate %{buildroot}%{_datadir}/xfce4/applications/xfdesktop.desktop

%find_lang %{name}

%files -f %{name}.lang
%license COPYING
%doc AUTHORS NEWS README.md
%{_bindir}/xfdesktop
%{_bindir}/xfdesktop-settings
%{_datadir}/applications/xfdesktop-settings.desktop
%{_datadir}/xfce4/applications/xfdesktop.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/pixmaps/*
%{_datadir}/backgrounds/xfce/
%{_mandir}/man1/xfdesktop.1*

%changelog
%autochangelog
