%{!?python_sitelib: %define python_sitelib %(/usr/bin/python2.4 -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%define pyver 2.4
%define py_incdir %{_includedir}/python%{pyver}

%define _default_patch_fuzz 2

Summary:       Python's own image processing library
Name:          compat-python24-imaging
Version:       1.1.6
Release:       3%{?dist}

License:       BSD
Group:         System Environment/Libraries

Source0:       http://effbot.org/downloads/Imaging-%{version}.tar.gz
Patch0:        compat-python-imaging-no-xv.patch
Patch1:        compat-python-imaging-lib64.patch
Patch2:        compat-python-imaging-giftrans.patch
Patch3:        compat-python-imaging-1.1.6-sane-types.patch
URL:           http://www.pythonware.com/products/pil/
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: compat-python24-devel, libjpeg-devel, zlib-devel, freetype-devel
BuildRequires: compat-tkinter24, tk-devel
BuildRequires: sane-backends-devel
Requires: python(abi) = 2.4

%description
Python Imaging Library

The Python Imaging Library (PIL) adds image processing capabilities
to your Python interpreter.

This library provides extensive file format support, an efficient
internal representation, and powerful image processing capabilities.

Details about licensing can be found from README file.

%package devel
Summary: Development files for python-imaging
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}, compat-python24-devel
Requires: libjpeg-devel
Requires: zlib-devel

%description devel
Development files for python-imaging.

%package sane
Summary: Python Module for using scanners
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description sane
This package contains the sane module for Python which provides access to
various raster scanning devices such as flatbed scanners and digital cameras.

%package tk
Summary: Tk interface for python-imaging
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}
Requires: compat-tkinter24

%description tk
This package contains a Tk interface for python-imaging.

%prep
%setup -q -n Imaging-%{version}
%patch0 -p1
%patch1 -p0
%patch2 -p1
%patch3 -p1 -b .sane-types

# fix the interpreter path for Scripts/*.py
cd Scripts
for scr in *.py
do
  sed -e "s|/usr/local/bin/python|%{_bindir}/python2.4|"  $scr > tmp.py
  mv tmp.py $scr
  chmod 755 $scr
done

%build
# Is this still relevant? (It was used in 1.1.4)
#%ifarch x86_64
#   CFLAGS="$RPM_OPT_FLAGS -fPIC -DPIC" \
#%endif

CFLAGS="$RPM_OPT_FLAGS" %{_bindir}/python2.4 setup.py build

pushd Sane
CFLAGS="$RPM_OPT_FLAGS" %{_bindir}/python2.4 setup.py build
popd

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{py_incdir}/Imaging
install -m 644 libImaging/*.h $RPM_BUILD_ROOT/%{py_incdir}/Imaging
%{_bindir}/python2.4 setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

pushd Sane
%{_bindir}/python2.4 setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd

# There is no need to ship the binaries since they are already packaged
# in %doc
rm -rf $RPM_BUILD_ROOT%{_bindir}

# Separate files that need Tk and files that don't
echo '%%defattr (0644,root,root,755)' > files.main
echo '%%defattr (0644,root,root,755)' > files.tk
p="$PWD"

pushd $RPM_BUILD_ROOT%{python_sitelib}/PIL
for file in *; do
    case "$file" in
    ImageTk*|SpiderImagePlugin*|_imagingtk.so)
        what=files.tk
        ;;
    *)
        what=files.main
        ;;
    esac
    echo %{python_sitelib}/PIL/$file >> "$p/$what"
done
popd
        

%check
PYTHONPATH=$(ls -1d build/lib.linux*) %{_bindir}/python2.4 selftest.py

%clean
rm -rf $RPM_BUILD_ROOT


%files -f files.main
%defattr (-,root,root)
%doc README CHANGES
%{python_sitelib}/PIL.pth
%dir %{python_sitelib}/PIL

%files devel
%defattr (0644,root,root,755)
%{py_incdir}/Imaging
%doc Docs Scripts Images

%files sane
%defattr (0644,root,root,755)
%doc Sane/CHANGES Sane/demo*.py Sane/sanedoc.txt
%{python_sitelib}/_sane.so
%{python_sitelib}/sane.py*

%files tk -f files.tk

%changelog
* Sun Sep 28 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 1.1.6-3
- add _default_patch_fuzz 2
- remove || : after check

* Sun Aug 10 2008 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info - 1.1.6-2
- rebuild for RPM Fusion

* Mon Jun 18 2007 Jonathan Steffan <jon a fedoraunity.org> 1.1.6-1
- Initial build from fc6 srpm
