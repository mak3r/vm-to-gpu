Name: vm-to-gpu
Version: 1.0
Release: 1%{?dist}
Summary: A GUI tool for managing VM USB passthrough
License: GPLv3
Group: System/Utilities
URL: https://github.com/yourusername/vm-to-gpu
Source0: %{name}-%{version}.tar.gz

BuildArch: noarch
Requires: python3, gtk3, libnotify

%description
A minimal GTK-based GUI for managing USB passthrough in virtual machines.

%prep
%setup -q -n %{name}-%{version}

%install
mkdir -p %{buildroot}/usr/local/bin
install -m 755 src/main.py %{buildroot}/usr/local/bin/vm-to-gpu
mkdir -p %{buildroot}/usr/local/lib/python3.x/site-packages/vm_to_gpu
install -m 755 src/vm_to_gpu/__init__.py %{buildroot}/usr/local/lib/python3.x/site-packages/vm_to_gpu/
install -m 755 src/vm_to_gpu/left_ui.py %{buildroot}/usr/local/lib/python3.x/site-packages/vm_to_gpu/
install -m 755 src/vm_to_gpu/right_ui.py %{buildroot}/usr/local/lib/python3.x/site-packages/vm_to_gpu/
install -m 755 src/vm_to_gpu/buttons.py %{buildroot}/usr/local/lib/python3.x/site-packages/vm_to_gpu/
install -m 755 src/vm_to_gpu/config_manager.py %{buildroot}/usr/local/lib/python3.x/site-packages/vm_to_gpu/

mkdir -p %{buildroot}/usr/share/applications
install -m 644 packaging/vm-to-gpu.desktop %{buildroot}/usr/share/applications/

mkdir -p %{buildroot}/var/log/vm-to-gpu

%files
/usr/local/bin/vm-to-gpu
/usr/local/lib/python3.x/site-packages/vm_to_gpu/__init__.py
/usr/local/lib/python3.x/site-packages/vm_to_gpu/left_ui.py
/usr/local/lib/python3.x/site-packages/vm_to_gpu/right_ui.py
/usr/local/lib/python3.x/site-packages/vm_to_gpu/buttons.py
/usr/local/lib/python3.x/site-packages/vm_to_gpu/config_manager.py
/usr/share/applications/vm-to-gpu.desktop
/var/log/vm-to-gpu

%changelog
* Wed March 12 2025 Your Name <your@email.com> - 1.0-1
- Initial release