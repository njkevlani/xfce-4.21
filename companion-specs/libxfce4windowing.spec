%global xfceversion 4.20
%global api_majorver 0

Name:           libxfce4windowing
Version:        4.20.7
Release:        %autorelease
Summary:        Windowing concept abstraction library for X11 and Wayland

License:        LGPL-2.1-or-later
URL:            https://docs.xfce.org/xfce/libxfce4windowing/start
Source0:        https://archive.xfce.org/src/xfce/%{name}/%{xfceversion}/%{name}-%{version}.tar.bz2

BuildRequires:  gcc
BuildRequires:  meson >= 0.56.0
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(glib-2.0) >= 2.68.0
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.68.0
BuildRequires:  pkgconfig(gtk+-3.0) >= 3.24.10
BuildRequires:  pkgconfig(gdk-pixbuf-2.0) >= 2.40.8
BuildRequires:  pkgconfig(wayland-client) >= 1.20
BuildRequires:  pkgconfig(wayland-protocols) >= 1.25
BuildRequires:  pkgconfig(wayland-scanner) >= 1.20
BuildRequires:  pkgconfig(wlr-protocols)
BuildRequires:  pkgconfig(gdk-wayland-3.0) >= 3.24.10
BuildRequires:  pkgconfig(gdk-x11-3.0) >= 3.24.10
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xrandr) >= 1.5.0
BuildRequires:  pkgconfig(libwnck-3.0) >= 3.10
BuildRequires:  pkgconfig(libdisplay-info) >= 0.1.1
BuildRequires:  gobject-introspection-devel
BuildRequires:  vala

%description
An abstraction library that presents windowing concepts (screens, monitors,
desktops, windows) in a unified way for X11 and Wayland display servers.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package includes development files and documentation for %{name}.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%meson \
    -Dx11=enabled \
    -Dwayland=enabled \
    -Dgtk-doc=false \
    -Dtests=false
%meson_build

%install
%meson_install
%find_lang %{name}

%files -f %{name}.lang
%license COPYING
%doc AUTHORS NEWS
%{_libdir}/libxfce4windowing-0.so.*
%{_libdir}/libxfce4windowing-x11-0.so.*
%{_libdir}/libxfce4windowingui-0.so.*
%{_libdir}/girepository-1.0/Libxfce4windowing*-%{api_majorver}.0.typelib

%files devel
%{_includedir}/xfce4/libxfce4windowing/
%{_includedir}/xfce4/libxfce4windowingui/
%{_libdir}/libxfce4windowing-0.so
%{_libdir}/libxfce4windowing-x11-0.so
%{_libdir}/libxfce4windowingui-0.so
%{_libdir}/pkgconfig/libxfce4windowing-0.pc
%{_libdir}/pkgconfig/libxfce4windowing-x11-0.pc
%{_libdir}/pkgconfig/libxfce4windowingui-0.pc
%{_datadir}/gir-1.0/Libxfce4windowing*-%{api_majorver}.0.gir
%{_datadir}/vala/vapi/libxfce4windowing*

%changelog
%autochangelog
