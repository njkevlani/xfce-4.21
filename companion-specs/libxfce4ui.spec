%global xfceversion 4.21

Name:           libxfce4ui
Version:        4.21.9
Release:        %autorelease
Summary:        Commonly used Xfce widgets and helper functions

License:        LGPL-2.0-or-later
URL:            https://docs.xfce.org/xfce/libxfce4ui/start
Source0:        https://archive.xfce.org/src/xfce/%{name}/%{xfceversion}/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  meson >= 0.61.0
BuildRequires:  ninja-build
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(glib-2.0) >= 2.72.0
BuildRequires:  pkgconfig(gtk+-3.0) >= 3.24.0
BuildRequires:  pkgconfig(gdk-pixbuf-2.0) >= 2.42.8
BuildRequires:  pkgconfig(libxfce4util-1.0) >= 4.21.0
BuildRequires:  pkgconfig(libxfconf-0) >= 4.12.0
BuildRequires:  pkgconfig(libstartup-notification-1.0) >= 0.4
BuildRequires:  pkgconfig(gudev-1.0) >= 232
BuildRequires:  pkgconfig(libgtop-2.0) >= 2.24.0
BuildRequires:  pkgconfig(epoxy) >= 1.2
BuildRequires:  libSM-devel
BuildRequires:  libICE-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  vala

%description
Commonly used Xfce widgets and desktop integration functions.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package includes development files and headers for %{name}.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%meson \
    -Dgtk-doc=false \
    -Dtests=false
%meson_build

%install
%meson_install
%find_lang %{name}

%files -f %{name}.lang
%license COPYING
%doc AUTHORS NEWS
%{_bindir}/xfce4-about
%{_libdir}/libxfce4ui-2.so.*
%{_libdir}/libxfce4kbd-private-3.so.*
%{_libdir}/girepository-1.0/Libxfce4ui-2.0.typelib
%{_datadir}/applications/xfce4-about.desktop
%{_datadir}/icons/hicolor/*/*/*

%files devel
%{_includedir}/xfce4/libxfce4ui-2/
%{_includedir}/xfce4/libxfce4kbd-private-3/
%{_libdir}/libxfce4ui-2.so
%{_libdir}/libxfce4kbd-private-3.so
%{_libdir}/pkgconfig/libxfce4ui-2.pc
%{_libdir}/pkgconfig/libxfce4kbd-private-3.pc
%{_datadir}/gir-1.0/Libxfce4ui-2.0.gir
%{_datadir}/vala/vapi/libxfce4ui-2.vapi

%changelog
%autochangelog
