Name:           system76-scheduler
Version:        2.{{{ git_dir_version }}}
Release:        1%{?dist}
Summary:        Oneshot service to tweak the CFS scheduler on boot. Uses settings from the TKG kernel by default.

License:        MPLv2.0
URL:            https://github.com/KyleGospo/system76-scheduler

VCS:            {{{ git_dir_vcs }}}
Source:         {{{ git_dir_pack }}}

# Realtime priority if bcc-tools is installed. Not available on OpenMandriva.
%if ! 0%{?mdkversion}
Requires:       bcc-tools
%endif

# No just package on EPEL, OpenSUSE, or OpenMandriva
%{?fedora:BuildRequires:  just}
BuildRequires:  rust
BuildRequires:  cargo
BuildRequires:  pipewire-devel
BuildRequires:  llvm-devel
BuildRequires:  clang-libs
BuildRequires:  clang-devel
BuildRequires:  systemd
BuildRequires:  systemd-rpm-macros  
# Required packages to build just on OpenMandriva
%if 0%{?mdkversion}
BuildRequires:  glibc-devel
BuildRequires:  glibc-static-devel
%endif

%description
Scheduling service which optimizes Linux's CPU scheduler and automatically assigns process priorities for improved desktop responsiveness. Low latency CPU scheduling will be activated automatically when on AC, and the default scheduling latencies set on battery. Processes are regularly sweeped and assigned process priorities based on configuration files. When combined with a supported desktop environment, foreground processes and their sub-processes will be given higher process priority.

These changes result in a noticeable improvement in the experienced smoothness and performance of applications and games. The improved responsiveness of applications is most noticeable on older systems with budget hardware, whereas games will benefit from higher framerates and reduced jitter. This is because background applications and services will be given a smaller portion of leftover CPU budget after the active process has had the most time on the CPU.

# Disable debug packages
%define debug_package %{nil}
%if 0%{?mdkversion}
# FIXME this is a workaround for some debug files being created on OpenMandriva despite debug_package being set to %{nil}
%define _unpackaged_files_terminate_build 0
%endif

# Set path to just
%if ! 0%{?fedora}
# Cargo install path on EPEL, OpenSUSE, or OpenMandriva
%define justpath /builddir/.cargo/bin/just
%else
%define justpath just
%endif

%prep
{{{ git_dir_setup_macro }}}

# This will invoke `just` command in the directory with the extracted sources.
%build
%if ! 0%{?fedora}
cargo install just
%endif
%{justpath} execsnoop=/usr/share/bcc/tools/execsnoop build-release

# This will copy the files generated by the `just` command above into
# the installable rpm package.
%install
%{justpath} rootdir=%{buildroot} unitdir=%{_unitdir} sysconfdir=%{_sysconfdir} install

# Do post-installation
%post
%systemd_post com.system76.Scheduler.service

# Do before uninstallation
%preun
%systemd_preun com.system76.Scheduler.service

# Do after uninstallation
%postun
%systemd_postun_with_restart com.system76.Scheduler.service

# This lists all the files that are included in the rpm package and that
# are going to be installed into target system where the rpm is installed.
%files
%license LICENSE
%doc README.md
%{_bindir}/system76-scheduler
%{_sysconfdir}/system76-scheduler/config.kdl
%{_sysconfdir}/system76-scheduler/process-scheduler/rhel.kdl
%{_unitdir}/com.system76.Scheduler.service
%{_sysconfdir}/dbus-1/system.d/com.system76.Scheduler.conf

# Finally, changes from the latest release of your application are generated from
# your project's Git history. It will be empty until you make first annotated Git tag.
%changelog
{{{ git_dir_changelog }}}
