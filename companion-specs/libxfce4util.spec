%global xfceversion 4.21

Name:           libxfce4util
Version:        4.21.0
Release:        %autorelease
Summary:        Basic utility library for the Xfce4 desktop environment

License:        LGPL-2.0-or-later
URL:            https://docs.xfce.org/xfce/libxfce4util/start
Source0:        https://archive.xfce.org/src/xfce/%{name}/%{xfceversion}/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  meson >= 0.56.0
BuildRequires:  ninja-build
BuildRequires:  gettext
BuildRequires:  pkgconfig(glib-2.0) >= 2.72.0
BuildRequires:  gobject-introspection-devel
BuildRequires:  vala
BuildRequires:  gtk-doc

%description
This package includes basic utility non-GUI functions for Xfce4.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       glib2-devel%{?_isa}

%description    devel
This package includes development files and documentation for %{name}.

%prep
%autosetup -p1 -n %{name}-%{version}

%build
%meson -Dgtk-doc=false
%meson_build

%install
%meson_install
%find_lang %{name}

%files -f %{name}.lang
%license COPYING
%doc AUTHORS NEWS
%{_libdir}/libxfce4util.so.*
%{_libdir}/girepository-1.0/Libxfce4util-1.0.typelib

%files devel
%{_includedir}/xfce4/libxfce4util/
%{_libdir}/libxfce4util.so
%{_libdir}/pkgconfig/libxfce4util-1.0.pc
%{_datadir}/gir-1.0/Libxfce4util-1.0.gir
%{_datadir}/vala/vapi/libxfce4util-1.0.vapi

%changelog
%autochangelog
