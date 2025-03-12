SHELL=/bin/bash
BUILDDIR=rpmbuild/RPMS/noarch
APPNAME=vm-to-gpu
VERSION=1.0

all:
	@echo "Run 'make install' to install the application."

install: rpm
	rpm -i $(BUILDDIR)/$(APPNAME)-$(VERSION)-1.noarch.rpm
	@echo "Installation complete."

uninstall:
	rpm -e $(APPNAME)
	@echo "Uninstallation complete."

rpm:
	mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	tar -czf rpmbuild/SOURCES/$(APPNAME)-$(VERSION).tar.gz --transform "s,^,$(APPNAME)-$(VERSION)/," src packaging
	rpmbuild -bb --define "_version $(VERSION)" --define "_topdir `pwd`/rpmbuild" packaging/$(APPNAME).spec

container:
	podman build -t claude-code:$(APPNAME) .
	- podman volume create vm-to-gpu_volume

code-ai: container
	podman run --rm -it -v vm-to-gpu_volume:/app -v run:/usr/local/bin/ claude-code:$(APPNAME)

clean:
	rm -rf rpmbuild/*


.PHONY: all install uninstall rpm clean