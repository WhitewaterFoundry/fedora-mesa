# When bootstrapping an arch, omit the -demos subpackage.

# Architechture specific configuration.  FIXME:  Should build with DRI support
# everywhere, and select target is some other more pleasant fashion.

%ifarch s390 s390x
%define with_dri 0
%define dri_target linux-indirect
%else
%define with_dri 1
%endif

%ifarch %{ix86}
%define dri_target linux-dri-x86
%endif

%ifarch x86_64
%define dri_target linux-dri-x86-64
%endif

%ifarch ppc ppc64
%define dri_target linux-dri-ppc
%endif

# rpm sure has a funny way of spelling %ifndef.  This is the default case.
%if 0%{!?dri_target:1}
%define dri_target linux-dri
%endif

%define manpages gl-manpages-1.0.1

Summary: Mesa graphics libraries
Name: mesa
Version: 7.0.2
Release: 1%{?dist}
License: MIT
Group: System Environment/Libraries
URL: http://www.mesa3d.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0: http://internap.dl.sourceforge.net/sourceforge/mesa3d/MesaLib-%{version}.tar.bz2
Source1: http://internap.dl.sourceforge.net/sourceforge/mesa3d/MesaDemos-%{version}.tar.bz2
Source2: %{manpages}.tar.bz2

Patch0: mesa-7.0-build-config.patch
Patch4: mesa-6.5-dont-libglut-me-harder-ok-thx-bye.patch
Patch5: mesa-6.5.2-xserver-1.1-source-compat.patch
Patch18: mesa-7.0-selinux-awareness.patch
Patch23: mesa-6.5.2-bindcontext-paranoia.patch
Patch25: mesa-7.0-symlinks-before-depend.patch
Patch26: mesa-7.0.1-stable-branch.patch
Patch27: mesa-7.0-use_master-r300.patch
Patch28: mesa-7.0.1-r300-fix-writemask.patch
Patch29: mesa-7.0.1-r200-settexoffset.patch
Patch30: mesa-7.0.2-rx00-vertprog-num-temps-off-by-one.patch
Patch31: mesa-7.0.2-t_vp_build-use-less-temps.patch

BuildRequires: pkgconfig
%if %{with_dri}
BuildRequires: libdrm-devel >= 2.3.0-1
%endif
BuildRequires: libXxf86vm-devel
BuildRequires: expat-devel >= 2.0
BuildRequires: xorg-x11-proto-devel >= 7.1-8
BuildRequires: makedepend
BuildRequires: libselinux-devel
BuildRequires: libXext-devel
BuildRequires: freeglut-devel
BuildRequires: libXfixes-devel
BuildRequires: libXdamage-devel

%description
Mesa

%package libGL
Summary: Mesa libGL runtime libraries and DRI drivers
Group: System Environment/Libraries
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Provides: libGL
Obsoletes: Mesa XFree86-libs XFree86-Mesa-libGL xorg-x11-Mesa-libGL
Obsoletes: xorg-x11-libs
%if %{with_dri}
Requires: libdrm >= 2.3.0
%endif

%description libGL
Mesa libGL runtime libraries and DRI drivers.


%package libGL-devel
Summary: Mesa libGL development package
Group: Development/Libraries
Requires: mesa-libGL = %{version}-%{release}
Requires: libX11-devel
Provides: libGL-devel
Obsoletes: Mesa-devel XFree86-devel xorg-x11-devel
Conflicts: xorg-x11-proto-devel <= 7.2-12

%description libGL-devel
Mesa libGL development package


%package libGLU
Summary: Mesa libGLU runtime library
Group: System Environment/Libraries
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Provides: libGLU
Obsoletes: Mesa XFree86-libs XFree86-Mesa-libGLU xorg-x11-Mesa-libGLU
Obsoletes: xorg-x11-libs

%description libGLU
Mesa libGLU runtime library


%package libGLU-devel
Summary: Mesa libGLU development package
Group: Development/Libraries
Requires: mesa-libGLU = %{version}-%{release}
Requires: libGL-devel
Provides: libGLU-devel
Obsoletes: Mesa-devel XFree86-devel xorg-x11-devel

%description libGLU-devel
Mesa libGLU development package


%package libOSMesa
Summary: Mesa offscreen rendering libraries
Group: System Environment/Libraries
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Provides: libOSMesa

%description libOSMesa
Mesa offscreen rendering libraries


%package libOSMesa-devel
Summary: Mesa offscreen rendering development package
Group: Development/Libraries
Requires: mesa-libOSMesa = %{version}-%{release}

%description libOSMesa-devel
Mesa offscreen rendering development package


%package source
Summary: Mesa source code required to build X server
Group: Development/Libraries

%description source
The mesa-source package provides the minimal source code needed to
build DRI enabled X servers, etc.


%package -n glx-utils
Summary: GLX utilities
Group: Development/Libraries

%description -n glx-utils
The glx-utils package provides the glxinfo and glxgears utilities.


%package demos
Summary: Mesa demos
Group: Development/Libraries

%description demos
This package provides some demo applications for testing Mesa.


%prep
%setup -q -n Mesa-%{version} -b1 -b2
chmod a-x progs/demos/glslnoise.c

%patch0 -p1 -b .build-config
%patch4 -p0 -b .dont-libglut-me-harder-ok-thx-bye
%patch5 -p1 -b .xserver-1.1-compat
%patch18 -p1 -b .selinux-awareness
%patch23 -p1 -b .bindcontext
%patch25 -p1 -b .makej
%patch27 -p1 -b .r300
%patch28 -p1 -b .r300-writemask
%patch30 -p1 -b .rx00-fix-vp
%patch31 -p1 -b .vp-temp-fix

# WARNING: The following files are copyright "Mark J. Kilgard" under the GLUT
# license and are not open source/free software, so we remove them.
rm -f include/GL/uglglutshapes.h

# Hack the demos to use installed data files
sed -i -e 's,../images,%{_libdir}/mesa-demos-data,' progs/demos/*.c
sed -i -e 's,geartrain.dat,%{_libdir}/mesa-demos-data/geartrain.dat,' progs/demos/geartrain.c
sed -i -e 's,isosurf.dat,%{_libdir}/mesa-demos-data/isosurf.dat,' progs/demos/isosurf.c
sed -i -e 's,"terrain.dat","%{_libdir}/mesa-demos-data/terrain.dat",' progs/demos/terrain.c

%build

# The i965 DRI driver breaks if compiled with -O2.  It appears to be
# an aliasing problem, so we add -fno-strict-aliasing to the flags.
export OPT_FLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -fvisibility=hidden -fPIC"
export DRI_DRIVER_DIR="%{_libdir}/dri"
export LIB_DIR=%{_lib}

mkdir preserve

for t in osmesa osmesa16 osmesa32; do
    echo "Building $t"
    make %{?_smp_mflags} linux-$t
    mv %{_lib}/* preserve
    make -s realclean
done

echo "Building %{dri_target}"
make %{?_smp_mflags} %{dri_target}
make -C progs/xdemos glxgears glxinfo
make -C progs/demos
mv preserve/* %{_lib}
ln -s libOSMesa.so.6 %{_lib}/libOSMesa.so 
ln -s libOSMesa16.so.6 %{_lib}/libOSMesa16.so
ln -s libOSMesa32.so.6 %{_lib}/libOSMesa32.so

pushd .
cd ../%{manpages}
%configure
make %{?_smp_mflags}
popd


%install
rm -rf $RPM_BUILD_ROOT

# The mesa build system is broken beyond repair.  The lines below just
# handpick and manually install the parts we want.

install -d $RPM_BUILD_ROOT%{_includedir}/GL
install -m 644 include/GL/{gl,o,x}*.h $RPM_BUILD_ROOT%{_includedir}/GL
install -d $RPM_BUILD_ROOT%{_includedir}/GL/internal
install -m 644 include/GL/internal/dri_interface.h $RPM_BUILD_ROOT%{_includedir}/GL/internal
rm -f $RPM_BUILD_ROOT%{_includedir}/GL/glfbdev.h

install -d $RPM_BUILD_ROOT%{_libdir}
cp -d -f %{_lib}/lib* $RPM_BUILD_ROOT%{_libdir}

install -d $RPM_BUILD_ROOT%{_bindir}
install -m 0755 progs/xdemos/glxgears $RPM_BUILD_ROOT%{_bindir}
install -m 0755 progs/xdemos/glxinfo $RPM_BUILD_ROOT%{_bindir}

find progs/demos/ -type f -perm /0111 |
    xargs install -m 0755 -t $RPM_BUILD_ROOT/%{_bindir}
install -d $RPM_BUILD_ROOT/%{_libdir}/mesa-demos-data
install -m 0644 progs/images/*.rgb $RPM_BUILD_ROOT/%{_libdir}/mesa-demos-data
install -m 0644 progs/demos/*.dat $RPM_BUILD_ROOT/%{_libdir}/mesa-demos-data

%if %{with_dri}
install -d $RPM_BUILD_ROOT%{_libdir}/dri
for f in i810 i915 i915tex i965 mach64 mga r128 r200 r300 radeon savage sis tdfx unichrome; do
    so=%{_lib}/${f}_dri.so
    test -e $so && echo $so
done | xargs install -m 0755 -t $RPM_BUILD_ROOT%{_libdir}/dri >& /dev/null || :
%endif

# Install man pages
pushd .
cd ../%{manpages}
make install DESTDIR=$RPM_BUILD_ROOT
popd

# Install the source needed to build the X server.  The egreps are just
# stripping out unnecessary dirs; only tricky bit is the [^c] to make sure
# .../dri/common is included.
%define mesasourcedir %{_datadir}/mesa/source
mkdir -p $RPM_BUILD_ROOT/%{mesasourcedir}
( find src -name \*.[ch] ; find include -name \*.h ) |
    egrep -v '^src/(glu|glw)' |
    egrep -v '^src/mesa/drivers/(directfb|dos|fbdev|glide|ggi|osmesa)' |
    egrep -v '^src/mesa/drivers/(windows|dri/[^c])' |
    xargs tar cf - --mode a=r |
	(cd $RPM_BUILD_ROOT/%{mesasourcedir} && tar xf -)


%clean
rm -rf $RPM_BUILD_ROOT


%check

%post libGL -p /sbin/ldconfig
%postun libGL -p /sbin/ldconfig
%post libGLU -p /sbin/ldconfig
%postun libGLU -p /sbin/ldconfig
%post libOSMesa -p /sbin/ldconfig
%postun libOSMesa -p /sbin/ldconfig

%files libGL
%defattr(-,root,root,-)
%{_libdir}/libGL.so.1
%{_libdir}/libGL.so.1.2

%if %{with_dri}
%dir %{_libdir}/dri
%{_libdir}/dri/*_dri.so
%endif

%files libGL-devel
%defattr(-,root,root,-)
%{_includedir}/GL/gl.h
%{_includedir}/GL/gl_mangle.h
%{_includedir}/GL/glext.h
%{_includedir}/GL/glx.h
%{_includedir}/GL/glx_mangle.h
%{_includedir}/GL/glxext.h
%{_includedir}/GL/xmesa.h
%{_includedir}/GL/xmesa_x.h
%{_includedir}/GL/xmesa_xf86.h
%dir %{_includedir}/GL/internal
%{_includedir}/GL/internal/dri_interface.h
%{_libdir}/libGL.so
%{_datadir}/man/man3/gl[^uX]*.3gl.gz
%{_datadir}/man/man3/glX*.3gl.gz

%files libGLU
%defattr(-,root,root,-)
%{_libdir}/libGLU.so.1
%{_libdir}/libGLU.so.1.3.*

%files libGLU-devel
%defattr(-,root,root,-)
%{_libdir}/libGLU.so
%{_includedir}/GL/glu.h
%{_includedir}/GL/glu_mangle.h
%{_datadir}/man/man3/glu*.3gl.gz

%files libOSMesa
%defattr(-,root,root,-)
%{_libdir}/libOSMesa.so.6
%{_libdir}/libOSMesa.so.6.5.3
%{_libdir}/libOSMesa16.so.6
%{_libdir}/libOSMesa16.so.6.5.3
%{_libdir}/libOSMesa32.so.6
%{_libdir}/libOSMesa32.so.6.5.3

%files libOSMesa-devel
%defattr(-,root,root,-)
%{_includedir}/GL/osmesa.h
%{_libdir}/libOSMesa.so
%{_libdir}/libOSMesa16.so
%{_libdir}/libOSMesa32.so

# We constructed this dir carefully, so just slurp in the whole thing.
%files source
%defattr(-,root,root,-)
%{mesasourcedir}

%files -n glx-utils
%defattr(-,root,root,-)
%{_bindir}/glxgears
%{_bindir}/glxinfo

%files demos
%defattr(-,root,root,-)
%{_bindir}/arbfplight
%{_bindir}/arbfslight
%{_bindir}/arbocclude
%{_bindir}/bounce
%{_bindir}/clearspd
%{_bindir}/cubemap
%{_bindir}/drawpix
%{_bindir}/engine
%{_bindir}/fire
%{_bindir}/fogcoord
%{_bindir}/fplight
%{_bindir}/fslight
%{_bindir}/gamma
%{_bindir}/gearbox
%{_bindir}/gears
%{_bindir}/geartrain
%{_bindir}/glinfo
%{_bindir}/gloss
%{_bindir}/glslnoise
%{_bindir}/gltestperf
%{_bindir}/glutfx
%{_bindir}/ipers
%{_bindir}/isosurf
%{_bindir}/lodbias
%{_bindir}/morph3d
%{_bindir}/multiarb
%{_bindir}/paltex
%{_bindir}/pointblast
%{_bindir}/ray
%{_bindir}/readpix
%{_bindir}/reflect
%{_bindir}/renormal
%{_bindir}/shadowtex
%{_bindir}/singlebuffer
%{_bindir}/spectex
%{_bindir}/spriteblast
%{_bindir}/stex3d
%{_bindir}/streaming_rect
%{_bindir}/teapot
%{_bindir}/terrain
%{_bindir}/tessdemo
%{_bindir}/texcyl
%{_bindir}/texdown
%{_bindir}/texenv
%{_bindir}/texobj
%{_bindir}/trispd
%{_bindir}/tunnel
%{_bindir}/tunnel2
%{_bindir}/vao_demo
%{_bindir}/winpos
%{_libdir}/mesa-demos-data

%changelog
* Tue Jan 01 2008 Dave Airlie <airlied@redhat.com> 7.0.2-1
- update to Mesa 7.0.2 final
- mesa-7.0.2-rx00-vertprog-num-temps-off-by-one.patch - fixes for maniadrive
- mesa-7.0.2-t_vp_build-use-less-temps.patch - fixes for maniadrive

* Thu Oct 18 2007 Dave Airlie <airlied@redhat.com> 7.0.1-7
- mesa-7.0.1-stable-branch.patch - Updated with more fixes from stable
- mesa-7.0.1-r300-fix-writemask.patch - fix r300 fragprog writemask
- mesa-7.0.1-r200-settexoffset.patch - add zero-copy TFP support for r200

* Fri Sep 28 2007 Dave Airlie <airlied@redhat.com> 7.0.1-6
- mesa-7.0.1-stable-branch.patch - Updated to close to 7.0.2-rc1
- This contains the fixes made to the upstream Mesa stable branch
  including fixes for 965 vblank interrupt issues along with a fix
  in the kernel - remove patches that already upstream.
- mesa-6.5.2-hush-synthetic-visual-warning.patch - dropped
- mesa-7.0-i-already-defined-glapi-you-twit.patch - dropped
- mesa-7.0.1-965-sampler-crash.patch - dropped

* Thu Sep 06 2007 Adam Jackson <ajax@redhat.com> 7.0.1-5
- mesa-7.0.1-965-sampler-crash.patch: Fix a crash with 965 in Torcs. (#262941)

* Tue Aug 28 2007 Adam Jackson <ajax@redhat.com> 7.0.1-4
- Rebuild for new libexpat.

* Wed Aug 15 2007 Dave Airlie <airlied@redhat.com> - 7.0.1-3
- mesa-7.0.1-stable-branch.patch - Add patches from stable branch
  includes support for some Intel chipsets
- mesa-7.0-use_master-r300.patch - Add r300 driver from master

* Tue Aug 14 2007 Dave Airlie <airlied@redhat.com> - 7.0.1-2
- missing build requires for Xfixes-devel and Xdamage-devel

* Mon Aug 13 2007 Dave Airlie <airlied@redhat.com> - 7.0.1-1
- Rebase to upstream 7.0.1 release
- ajax provided patches: for updated selinux awareness, build config
- gl visibility and picify were fixed upstream
- OS mesa library version are 6.5.3 not 7.0.1 - spec fix

* Wed Jul 25 2007 Jesse Keating <jkeating@redhat.com> - 6.5.2-16
- Rebuild for RH #249435

* Tue Jul 24 2007 Adam Jackson <ajax@redhat.com> 6.5.2-15
- Add dri_interface.h to mesa-libGL-devel, and conflict with
  xorg-x11-proto-devel versions that attempted to provide it.

* Tue Jul 10 2007 Adam Jackson <ajax@redhat.com> 6.5.2-14
- Add mesa-demos subpackage. (#247252)

* Mon Jul 09 2007 Adam Jackson <ajax@redhat.com> 6.5.2-13
- mesa-6.5.2-radeon-backports-231787.patch: One more fix for r300. (#231787)

* Mon Jul 09 2007 Adam Jackson <ajax@redhat.com> 6.5.2-12
- Don't install header files for APIs that we don't provide. (#247390)

* Fri Jul 06 2007 Adam Jackson <ajax@redhat.com> 6.5.2-11
- mesa-6.5.2-via-respect-my-cliplist.patch: Backport a via fix. (#247254)

* Tue Apr 10 2007 Adam Jackson <ajax@redhat.com> 6.5.2-10
- mesa-6.5.2-radeon-backports-231787.patch: Backport various radeon bugfixes
  from git. (#231787)

* Wed Apr 04 2007 Adam Jackson <ajax@redhat.com> 6.5.2-9
- mesa-6.5.2-bindcontext-paranoia.patch: Paper over a crash when doBindContext
  fails, to avoid, for example, crashing the server when using tdfx but
  without glide3 installed.

* Thu Mar 08 2007 Adam Jackson <ajax@redhat.com> 6.5.2-8
- Hush the (useless) warning about the synthetic visual not being supported.

* Fri Mar 02 2007 Adam Jackson <ajax@redhat.com> 6.5.2-7
- mesa-6.5.2-picify-dri-drivers.patch: Attempt to make the DRI drivers PIC.
- mesa-6.5.1-build-config.patch: Apply RPM_OPT_FLAGS to OSMesa too.

* Mon Feb 26 2007 Adam Jackson <ajax@redhat.com> 6.5.2-6
- mesa-6.5.2-libgl-visibility.patch: Fix non-exported GLX symbols (#229808)
- Require a sufficiently new libdrm at runtime too
- Make the arch macros do something sensible in the general case

* Tue Feb 20 2007 Adam Jackson <ajax@redhat.com> 6.5.2-5
- General spec cleanups
- Require current libdrm
- Build with -fvisibility=hidden
- Redo the way mesa-source is generated
- Add %%{?_smp_mflags} where appropriate

* Mon Dec 18 2006 Adam Jackson <ajax@redhat.com> 6.5.2-4
- Add i915tex and mach64 to the install set. 

* Tue Dec 12 2006 Adam Jackson <ajax@redhat.com> 6.5.2-3
- mesa-6.5.2-xserver-1.1-source-compat.patch: Add some source-compatibility
  defines to dispatch.h so the X server will continue to build.

* Mon Dec 4 2006 Adam Jackson <ajax@redhat.com> 6.5.2-2.fc6
- Fix OSMesa file listing to use %%version for DSO number.  Note that this
  will still break on Mesa 7; oh well.
- Deleted file: directfbgl.h

* Sun Dec  3 2006 Kristian Høgsberg <krh@redhat.com> 6.5.2-1.fc6
- Update to 6.5.2.

* Mon Oct 16 2006 Kristian <krh@redhat.com> - 6.5.1-8.fc6
- Add i965-interleaved-arrays-fix.patch to fix (#209318).

* Sat Sep 30 2006 Soren Sandmann <sandmann@redhat.com> - 6.5.1-7.fc6
- Update to gl-manpages-1.0.1.tar.bz2 which doesn't use symlinks. (#184547)

* Sat Sep 30 2006 Soren Sandmann <sandmann@redhat.com> - 6.5.1-7.fc6
- Remove . after popd; add .gz in %%files section. (#184547)

* Sat Sep 30 2006 Soren Sandmann <sandmann@redhat.com>
- Use better tarball for gl man pages. (#184547)

* Fri Sep 29 2006 Kristian <krh@redhat.com> - 6.5.1-6.fc6
- Add -fno-strict-aliasing to compiler flags for i965 driver.
- Add post-6.5.1-i965-fixes.patch backport of i965 fixes from mesa CVS.

* Fri Sep 29 2006 Soren Sandmann <sandamnn@redhat.com> - 6.5.1-5.fc6
- Give the correct path for man page file lists.

* Thu Sep 28 2006 Soren Sandmann <sandmann@redhat.com> - 6.5.1-5.fc6
- Add GL man pages from X R6.9.  (#184547)

* Mon Sep 25 2006 Adam Jackson <ajackson@redhat.com> - 6.5.1-4.fc6
- mesa-6.5.1-build-config.patch: Add -lselinux to osmesa builds.  (#207767)

* Wed Sep 20 2006 Kristian Høgsberg <krh@redhat.com> - 6.5.1-3.fc6
- Bump xorg-x11-proto-devel BuildRequires to 7.1-8 so we pick up the
  latest GLX_EXT_texture_from_pixmap opcodes.

* Wed Sep 20 2006 Kristian Høgsberg <krh@redhat.com> - 6.5.1-2.fc6
- Remove mesa-6.5-drop-static-inline.patch.

* Tue Sep 19 2006 Kristian Høgsberg <krh@redhat.com> 6.5.1-1.fc6
- Bump to 6.5.1 final release.
- Drop libGLw subpackage, it is now in Fedora Extras (#188974) and
  tweak mesa-6.5.1-build-config.patch to not build libGLw.
- Drop mesa-6.5.1-r300-smooth-line.patch, the smooth line fallback can
  now be prevented by enabling disable_lowimpact_fallback in
  /etc/drirc.
- Drop mesa-6.4.1-radeon-use-right-texture-format.patch, now upstream.
- Drop mesa-6.5-drop-static-inline.patch, workaround no longer necessary.

* Thu Sep  7 2006 Kristian Høgsberg <krh@redhat.com>
- Drop unused mesa-modular-dri-dir.patch.

* Tue Aug 29 2006 Kristian Høgsberg <krh@redhat.com> - 6.5.1-0.rc2.fc6
- Rebase to 6.5.1 RC2.
- Get rid of redhat-mesa-driver-install and redhat-mesa-target helper
  scripts and clean up specfile a bit.

* Mon Aug 28 2006 Kristian Høgsberg <krh@redhat.com> - 6.5.1-0.rc1.2.fc6
- Drop upstreamed patches mesa-6.5-texture-from-pixmap-fixes.patch and
  mesa-6.5-tfp-fbconfig-attribs.patch and fix
  mesa-6.4.1-radeon-use-right-texture-format.patch to not break 16bpp
  transparency.

* Fri Aug 25 2006 Adam Jackson <ajackson@redhat.com> - 6.5.1-0.rc1.1.fc6
- mesa-6.5.1-build-config.patch: Add i965 to x86-64 config.

* Wed Aug 23 2006 Kristian Høgsberg <krh@redhat.com> - 6.5.1-0.rc1.fc6
- Bump to 6.5.1 RC1.

* Tue Aug 22 2006 Kristian Høgsberg <krh@redhat.com> 6.5-26.20060818cvs.fc6
- Pull the vtxfmt patch into the selinux-awareness patch, handle exec
  mem heap init failure correctly by releasing mutex.

* Tue Aug 22 2006 Adam Jackson <ajackson@redhat.com> 6.5-25.20060818cvs.fc6
- mesa-6.5.1-r300-smooth-line.patch: Added, fakes smooth lines with aliased
  lines on R300+ cards, makes Google Earth tolerable.
- mesa-6.5-force-r300.patch: Resurrect.

* Tue Aug 22 2006 Adam Jackson <ajackson@redhat.com> 6.5-24.20060818cvs.fc6
- mesa-6.5.1-radeon-vtxfmt-cleanup-properly.patch: Fix a segfault on context
  destruction when selinux is enabled.

* Mon Aug 21 2006 Adam Jackson <ajackson@redhat.com> 6.5-23.20060818cvs.fc6
- redhat-mesa-driver-install: Reenable installing the tdfx driver. (#203295)

* Fri Aug 18 2006 Adam Jackson <ajackson@redhat.com> 6.5-22.20060818cvs.fc6
- Update to pre-6.5.1 snapshot.
- Re-add libOSMesa{,16,32}. (#186366)
- Add BuildReq: on libXp-devel due to openmotif header insanity.

* Sun Aug 13 2006 Florian La Roche <laroche@redhat.com> 6.5-21.fc6
- fix one Requires: to use the correct mesa-libGLw name

* Thu Jul 27 2006 Mike A. Harris <mharris@redhat.com> 6.5-20.fc6
- Conditionalized libGLw inclusion with new with_libGLw macro defaulting
  to 1 (enabled) for now, however since nothing in Fedora Core uses libGLw
  anymore, we will be transitioning libGLw to an external package maintained
  in Fedora Extras soon.

* Wed Jul 26 2006 Kristian Høgsberg <krh@redhat.com> 6.5-19.fc5.aiglx
- Build for fc5 aiglx repo.

* Tue Jul 25 2006 Adam Jackson <ajackson@redhat.com> 6.5-19.fc6
- Disable TLS dispatch, it is selinux-hostile.

* Tue Jul 25 2006 Adam Jackson <ajackson@redhat.com> 6.5-18.fc6
- mesa-6.5-fix-glxinfo-link.patch: lib64 fix.

* Tue Jul 25 2006 Adam Jackson <ajackson@redhat.com> 6.5-17.fc6
- mesa-6.5-fix-linux-indirect-build.patch: Added.
- mesa-6.5-fix-glxinfo-link.patch: Added.
- Build libOSMesa never instead of inconsistently; to be fixed later.
- Updates to redhat-mesa-target:
  - Always select linux-indirect when not building for DRI
  - Enable DRI to be built on PPC64 (still disabled in the spec file though)
  - MIT licence boilerplate

* Tue Jul 25 2006 Mike A. Harris <mharris@redhat.com> 6.5-16.fc6
- Remove glut-devel dependency, as nothing actually uses it that we ship.
- Added mesa-6.5-dont-libglut-me-harder-ok-thx-bye.patch to prevent libglut
  and other libs from being linked into glxgears/glxinfo even though they
  are not actually used.  This was the final package linking to freeglut in
  Fedora Core, blocking freeglut from being moved to Extras.
- Commented all of the virtual provides in the spec file to document clearly
  how they should be used by other developers in specifying build and runtime
  dependencies when packaging software which links to libGL, libGLU, and
  libGLw. (#200069)

* Mon Jul 24 2006 Adam Jackson <ajackson@redhat.com> 6.5-15.fc6
- Attempt to add selinux awareness; check if we can map executable memory
  and fail softly if not.  Removes the need for allow_execmem from huge
  chunks of the desktop.
- Disable the r300 gart fix for not compiling.

* Mon Jul 24 2006 Kristian Høgsberg <krh@redhat.com> 6.5-14.fc6
- Add mesa-6.5-r300-free-gart-mem.patch to make r300 driver free gart
  memory on context destroy.

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> 6.5-13.1.fc6
- rebuild

* Wed Jul 05 2006 Mike A. Harris <mharris@redhat.com> 6.5-13.fc6
- Added mesa-6.5-fix-opt-flags-bug197640.patch as 2nd attempt to fix OPT_FLAGS
  for (#197640).
- Ensure that redhat-mesa-driver-install creates $DRIMODULE_DESTDIR with
  mode 0755.

* Wed Jul 05 2006 Mike A. Harris <mharris@redhat.com> 6.5-12.fc6
- Maybe actually, you know, apply the mesa-6.5-glx-use-tls.patch as that might
  help to you know, actually solve the problem.  Duh.
- Use {dist} tag in Release field now.

* Wed Jul 05 2006 Mike A. Harris <mharris@redhat.com> 6.5-11
- Added mesa-6.5-glx-use-tls.patch to hopefully get -DGLX_USE_TLS to really
  work this time due to broken upstream linux-dri-* configs. (#193979)
- Pass RPM_OPT_FLAGS via OPT_FLAGS instead of via CFLAGS also for (#193979)

* Mon Jun 19 2006 Mike A. Harris <mharris@redhat.com> 6.5-10
- Bump libdrm-devel dep to trigger new ExclusiveArch test with the new package.
- Use Fedora Extras style BuildRoot tag.
- Added "Requires(post): /sbin/ldconfig" and postun to all runtime lib packages.

* Mon Jun 12 2006 Kristian Høsberg <krh@redhat.com> 6.5-9
- Add mesa-6.5-fix-pbuffer-dispatch.patch to fix pbuffer marshalling code.

* Mon May 29 2006 Kristian Høgsberg <krh@redhat.com> 6.5-8
- Bump for rawhide build.

* Mon May 29 2006 Kristian Høgsberg <krh@redhat.com> 6.5-7
- Update mesa-6.5-texture-from-pixmap-fixes.patch to include new
  tokens and change tfp functions to return void.  Yes, a new mesa
  snapshot would be nice.

* Wed May 17 2006 Mike A. Harris <mharris@redhat.com> 6.5-6
- Add "BuildRequires: makedepend" for bug (#191967)

* Tue Apr 11 2006 Kristian Høgsberg <krh@redhat.com> 6.5-5
- Bump for fc5 build.

* Tue Apr 11 2006 Adam Jackson <ajackson@redhat.com> 6.5-4
- Disable R300_FORCE_R300 hack for wider testing.

* Mon Apr 10 2006 Kristian Høgsberg <krh@redhat.com> 6.5-3
- Add mesa-6.5-noexecstack.patch to prevent assembly files from making
  libGL.so have executable stack.

* Mon Apr 10 2006 Kristian Høgsberg <krh@redhat.com> 6.5-2
- Bump for fc5 build.
- Bump libdrm requires to 2.0.1.

* Sat Apr 01 2006 Kristian Høgsberg <krh@redhat.com> 6.5-1
- Update to mesa 6.5 snapshot.
- Use -MG for generating deps and some files are not yet symlinked at
  make depend time.
- Drop mesa-6.4.2-dprintf-to-debugprintf-for-bug180122.patch and
  mesa-6.4.2-xorg-server-uses-bad-datatypes-breaking-AMD64-fdo5835.patch
  as these are upstream now.
- Drop mesa-6.4.1-texture-from-drawable.patch and add
  mesa-6.5-texture-from-pixmap-fixes.patch.
- Update mesa-modular-dri-dir.patch to apply.
- Widen libGLU glob.
- Reenable r300 driver install.
- Widen libOSMesa glob.
- Go back to patching config/linux-dri, add mesa-6.5-build-config.patch,
  drop mesa-6.3.2-build-configuration-v4.patch.
- Disable sis dri driver for now, only builds on x86 and x86-64.

* Fri Mar 24 2006 Kristian Høgsberg <krh@redhat.com> 6.4.2-7
- Set ARCH_FLAGS=-DGLX_USE_TLS to enable TLS for GL contexts.

* Wed Mar 01 2006 Karsten Hopp <karsten@redhat.de> 6.4.2-6
- Buildrequires: libXt-devel (#183479)

* Sat Feb 25 2006 Mike A. Harris <mharris@redhat.com> 6.4.2-5
- Disable the expeimental r300 DRI driver, as it has turned out to cause
  instability and system hangs for many users.

* Wed Feb 22 2006 Adam Jackson <ajackson@redhat.com> 6.4.2-4
- rebuilt

* Sun Feb 19 2006 Ray Strode <rstrode@redhat.com> 6.4.2-3
- enable texture-from-drawable patch
- add glut-devel dependency

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 6.4.2-2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Mike A. Harris <mharris@redhat.com> 6.4.2-2
- Added new "glx-utils" subpackage with glxgears and glxinfo (#173510)
- Added mesa-6.4.2-dprintf-to-debugprintf-for-bug180122.patch to workaround
  a Mesa namespace conflict with GNU_SOURCE (#180122)
- Added mesa-6.4.2-xorg-server-uses-bad-datatypes-breaking-AMD64-fdo5835.patch
  as an attempt to fix bugs (#176976,176414,fdo#5835)
- Enabled inclusion of the *EXPERIMENTAL UNSUPPORTED* r300 DRI driver on
  x86, x86_64, and ppc architectures, however the 2D Radeon driver will soon
  be modified to require the user to manually turn experimental DRI support
  on with Option "dri" in xorg.conf to test it out and report all X bugs that
  occur while using it directly to X.Org bugzilla.  (#179712)
- Use "libOSMesa.so.6.4.0604*" glob in file manifest, to avoid having to
  update it each upstream release.

* Sat Feb 04 2006 Mike A. Harris <mharris@redhat.com> 6.4.2-1
- Updated to Mesa 6.4.2
- Use "libGLU.so.1.3.0604*" glob in file manifest, to avoid having to update it
  each upstream release.

* Tue Jan 24 2006 Mike A. Harris <mharris@redhat.com> 6.4.1-5
- Added missing "BuildRequires: expat-devel" for bug (#178525)
- Temporarily disabled mesa-6.4.1-texture-from-drawable.patch, as it fails
  to compile on at least ia64, and possibly other architectures.

* Tue Jan 17 2006 Kristian Høgsberg <krh@redhat.com> 6.4.1-4
- Add mesa-6.4.1-texture-from-drawable.patch to implement protocol
  support for GLX_EXT_texture_from_drawable extension.

* Sat Dec 24 2005 Mike A. Harris <mharris@redhat.com> 6.4.1-3
- Manually copy libGLw headers that Mesa forgets to install, to fix (#173879).
- Added mesa-6.4.1-libGLw-enable-motif-support.patch to fix (#175251).
- Removed "Conflicts" lines from libGL package, as they are "Obsoletes" now.
- Do not rename swrast libGL .so version, as it is the OpenGL version.

* Tue Dec 20 2005 Mike A. Harris <mharris@redhat.com> 6.4.1-2
- Rebuild to ensure libGLU gets rebuilt with new gcc with C++ compiler fixes.
- Changed the 3 devel packages to use Obsoletes instead of Conflicts for the
  packages the files used to be present in, as this is more friendy for
  OS upgrades.
- Added "Requires: libX11-devel" to mesa-libGL-devel package (#173712)
- Added "Requires: libGL-devel" to mesa-libGLU-devel package (#175253)

* Sat Dec 17 2005 Mike A. Harris <mharris@redhat.com> 6.4.1-1
- Updated MesaLib tarball to version 6.4.1 from Mesa project for X11R7 RC4.
- Added pkgconfig dependency.
- Updated "BuildRequires: libdrm-devel >= 2.0-1"
- Added Obsoletes lines to all the subpackages to have cleaner upgrades.
- Added mesa-6.4.1-amd64-assyntax-fix.patch to work around a build problem on
  AMD64, which is fixed in the 6.4 branch of Mesa CVS.
- Conditionalize libOSMesa inclusion, and default to not including it for now.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com> 6.4-5.1
- rebuilt

* Sun Nov 20 2005 Jeremy Katz <katzj@redhat.com> 6.4-5
- fix directory used for loading dri modules (#173679)
- install dri drivers as executable so they get stripped (#173292)

* Thu Nov 03 2005 Mike A. Harris <mharris@redhat.com> 6.4-4
- Wrote redhat-mesa-source-filelist-generator to dynamically generate the
  files to be included in the mesa-source subpackage, to minimize future
  maintenance.
- Fixed detection and renaming of software mesa .so version.

* Wed Nov 02 2005 Mike A. Harris <mharris@redhat.com> 6.4-3
- Hack: autodetect if libGL was given .so.1.5* and rename it to 1.2 for
  consistency on all architectures, and to avoid upgrade problems if we
  ever disable DRI on an arch and then re-enable it later.

* Wed Nov 02 2005 Mike A. Harris <mharris@redhat.com> 6.4-2
- Added mesa-6.4-multilib-fix.patch to instrument and attempt to fix Mesa
  bin/installmesa script to work properly with multilib lib64 architectures.
- Set and export LIB_DIR and INCLUDE_DIR in spec file 'install' section,
  and invoke our modified bin/installmesa directly instead of using
  "make install".
- Remove "include/GL/uglglutshapes.h", as it uses the GLUT license, and seems
  like an extraneous file anyway.
- Conditionalize the file manifest to include libGL.so.1.2 on DRI enabled
  builds, but use libGL.so.1.5.060400 instead on DRI disabled builds, as
  this is how upstream builds the library, although it is not clear to me
  why this difference exists yet (which was not in Xorg 6.8.2 Mesa).

* Thu Oct 27 2005 Mike A. Harris <mharris@redhat.com> 6.4-1
- Updated to new upstream MesaLib-6.4
- Updated libGLU.so.1.3.060400 entry in file manifest
- Updated "BuildRequires: libdrm-devel >= 1.0.5" to pick up fixes for the
  unichrome driver.

* Tue Sep 13 2005 Mike A. Harris <mharris@redhat.com> 6.3.2-6
- Fix redhat-mesa-driver-install and spec file to work right on multilib
  systems.
  
* Mon Sep 05 2005 Mike A. Harris <mharris@redhat.com> 6.3.2-5
- Fix mesa-libGL-devel to depend on mesa-libGL instead of mesa-libGLU.
- Added virtual "Provides: libGL..." entries for each subpackage as relevant.

* Mon Sep 05 2005 Mike A. Harris <mharris@redhat.com> 6.3.2-4
- Added the mesa-source subpackage, which contains part of the Mesa source
  code needed by other packages such as the X server to build stuff.

* Mon Sep 05 2005 Mike A. Harris <mharris@redhat.com> 6.3.2-3
- Added Conflicts/Obsoletes lines to all of the subpackages to make upgrades
  from previous OS releases, and piecemeal upgrades work as nicely as
  possible.

* Mon Sep 05 2005 Mike A. Harris <mharris@redhat.com> 6.3.2-2
- Wrote redhat-mesa-target script to simplify mesa build target selection.
- Wrote redhat-mesa-driver-install to install the DRI drivers and simplify
  per-arch conditionalization, etc.

* Sun Sep 04 2005 Mike A. Harris <mharris@redhat.com> 6.3.2-1
- Initial build.
