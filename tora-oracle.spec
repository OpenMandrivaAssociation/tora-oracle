# This requires Oracle instant client installed
#
%define _use_internal_dependency_generator 0
%define tarball_name	tora
%define name	%{tarball_name}-oracle
%define version	2.1.1
%define release %mkrel 1

Summary:		Toolkit for Oracle with Oracle, MySQL and PostgreSQL support
Name:			%{name}
Version:		%{version}
Release:		%{release}
Source:			%{tarball_name}-%{version}.tar.bz2
Patch1:			fix_kde_theme_qt45.patch
URL:			http://www.torasql.com
Group:			Development/Databases
License:		GPLv2+
BuildRoot:		%{_tmppath}/tora-root
Requires:	qt4-common
Requires:	qt4-database-plugin-mysql
Requires:	qt4-database-plugin-pgsql
Requires:	libaio1
#Requires:	oracle-instantclient11.1-basic
BuildRequires:	kdelibs4-devel
BuildRequires:	postgresql-devel
BuildRequires:	qscintilla-qt4-devel
BuildRequires:	qt4-devel
#BuildRequires:	oracle-instantclient11.1-devel 
Conflicts:	tora
 
%description

TOra - Toolkit for Oracle, MySQL and PostgreSQL

TOra is a Toolkit for Oracle which aims to help the DBA or developer of 
database application. Features PL/SQL debugger, SQL worksheet with syntax 
highlighting, DB browser and a comprehensive set of DBA tools. TOra also 
includes support for MySQL and PostgeSQL.

This version of TOra is supported for running with an Oracle 10g or newer 
instant client installation.

ATTENTION: This package requires that you have installed and configured 
Oracle instant client to use TOra to connect to Oracle databases. 
You can download it from Oracle's website.

Oracle is copyright of Oracle Corporation.

%prep
# Ugly hack to avoid failed dependency on libclntsh
echo "%{__find_requires} $* | grep -v 'libclntsh*'" > %{_tmppath}/custom-findreqs.sh
chmod +x %{_tmppath}/custom-findreqs.sh
%define __find_requires %{_tmppath}/custom-findreqs.sh

%setup -q -n %{tarball_name}-%{version}
%patch1 -p1

%build
%cmake_kde4 -DPOSTGRESQL_PATH_LIB=%{_libdir}/postgresql/  \
	-DPOSTGRESQL_PATH_INCLUDES=%{_includedir}/postgresql/ \
	-DORACLE_PATH_LIB=%{_libdir}/oracle/11.1/client/lib/ \
	-DORACLE_PATH_INCLUDES=%{_includedir}/oracle/11.1/client/ \
	-DORACLE_OCI_VERSION=10G_R2
#Since tora 2.1.0 if don't export LD_LIBRARY_PATH before building it
#it will fail at the linking stage
export LD_LIBRARY_PATH=%{_libdir}/oracle/11.1/client/lib/
%make

%install
%makeinstall_std -C build

%find_lang %tarball_name

# menu
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/%{tarball_name}.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=TOra
Comment=Toolkit for Oracle
Exec=%{tarball_name}
Icon=%{tarball_name}
Terminal=false
Type=Application
X-KDE-StartupNotify=true
Categories=X-MandrivaLinux-MoreApplications-Databases;Database;KDE;Qt;
MimeType=application/x-tora;
EOF

%{__install} -D --mode=644 src/icons/tora.xpm "${RPM_BUILD_ROOT}%{_iconsdir}/hicolor/32x32/apps/tora.xpm"
%{__install} -D --mode=644 src/icons/toramini.xpm "${RPM_BUILD_ROOT}%{_iconsdir}/hicolor/16x16/apps/tora.xpm"
%{__install} -d $RPM_BUILD_ROOT%{_libdir}
%{__install} --mode=644 src/templates/*.tpl "${RPM_BUILD_ROOT}%{_libdir}/"

#Because this tora version depends on oracle libs we need to wrap the binary in a shell script that
#exports LD_LIBRARY_PATH to the location of oracle libs.
%{__mv} -T ${RPM_BUILD_ROOT}%{_bindir}/%{tarball_name} ${RPM_BUILD_ROOT}%{_bindir}/%{tarball_name}.real

cat > ${RPM_BUILD_ROOT}%{_bindir}/%{tarball_name} << EOF
#!/bin/sh
ORA_VER=\$(/bin/ls %{_libdir}/oracle 2>/dev/null)
if [ ! -d "%{_libdir}/oracle/\$ORA_VER/client" ]; then
        echo "Can't find Oracle client directory"
        echo "Please check your Oracle client installation"
        exit 1
fi
export ORACLE_HOME=%{_libdir}/oracle/\$ORA_VER/client
export LD_LIBRARY_PATH=\$ORACLE_HOME/lib:\$LD_LIBRARY_PATH
exec %{_bindir}/%{tarball_name}.real
EOF

cat > ${RPM_BUILD_ROOT}/%{_docdir}/tora/README.urpmi << EOF

ATTENTION: This package requires that you have installed and configured Oracle
instant client to be able to use this version of TOra. 

You can download Oracle instant client from:

http://www.oracle.com/technology/software/tech/oci/instantclient/htdocs/linuxsoft.html

If you don't need Oracle database support then please install tora package.

EOF

%post
%update_icon_cache hicolor

%postun
%clean_icon_cache hicolor

%files
%defattr(-,root,root)
%{_bindir}/*
%{_libdir}/*.tpl
%_datadir/applications/%{tarball_name}.desktop
%{_docdir}/tora/*
%{_iconsdir}/hicolor/*/apps/%{tarball_name}*.xpm

