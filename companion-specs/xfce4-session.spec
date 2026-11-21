%global xfceversion 4.21

Name:           xfce4-session
Version:        4.21.2
Release:        %autorelease
Summary:        Session manager and client library for the Xfce Desktop Environment

License:        GPL-2.0-or-later
URL:            https://docs.xfce.org/xfce/xfce4-session/start
Source0:        https://archive.xfce.org/src/xfce/%{name}/%{xfceversion}/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  meson >= 0.56.0
BuildRequires:  ninja-build
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  gobject-introspection-devel
BuildRequires:  vala
BuildRequires:  pkgconfig(glib-2.0) >= 2.76.0
BuildRequires:  pkgconfig(gtk+-3.0) >= 3.24.0
BuildRequires:  pkgconfig(libxfce4util-1.0) >= 4.21.0
BuildRequires:  pkgconfig(libxfce4ui-2) >= 4.21.0
BuildRequires:  pkgconfig(libxfce4windowing-0) >= 4.19.2
BuildRequires:  pkgconfig(libxfconf-0) >= 4.12.0
BuildRequires:  pkgconfig(gtk-layer-shell-0) >= 0.7.0
BuildRequires:  pkgconfig(wayland-client) >= 1.23
BuildRequires:  pkgconfig(wayland-protocols) >= 1.25
BuildRequires:  pkgconfig(wayland-scanner) >= 1.20
BuildRequires:  pkgconfig(gdk-wayland-3.0) >= 3.24.0
BuildRequires:  pkgconfig(gdk-x11-3.0) >= 3.24.0
BuildRequires:  pkgconfig(libwnck-3.0) >= 3.10.0
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  libSM-devel
BuildRequires:  libICE-devel
BuildRequires:  iceauth
BuildRequires:  xrdb
BuildRequires:  xset

Requires:       iceauth
Requires:       xrdb
Requires:       libxfce4ui%{?_isa} >= 4.21.0
Requires:       libxfce4util%{?_isa} >= 4.21.0

%description
This package includes the session manager and the libxfce4session-client
library for the Xfce Desktop Environment, supporting both X11 and Wayland sessions.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package includes development files and headers for %{name}.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%meson \
    -Dwayland=enabled \
    -Dx11=enabled \
    -Dgtk-doc=false
%meson_build

%install
%meson_install
%find_lang %{name}

%files -f %{name}.lang
%license COPYING
%doc AUTHORS NEWS
%{_bindir}/*
%{_libdir}/libxfce4session-client-1.so.*
%{_libdir}/girepository-1.0/*
%{_libdir}/xfce4/session/
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/*/*
%{_datadir}/polkit-1/actions/*
%{_datadir}/xdg-desktop-portal/*
%{_datadir}/xsessions/*
%{_datadir}/wayland-sessions/*
%{_datadir}/xfce4/
%{_sysconfdir}/xdg/xfce4/
%{_mandir}/man1/*

%files devel
%{_includedir}/xfce4/libxfce4session-client-1/
%{_libdir}/libxfce4session-client-1.so
%{_libdir}/pkgconfig/libxfce4session-client-1.pc
%{_datadir}/gir-1.0/*
%{_datadir}/vala/vapi/*

%changelog
%autochangelog
