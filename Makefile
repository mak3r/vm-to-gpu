PREFIX=/usr/local
BINDIR=$(PREFIX)/bin
APPNAME=vm-to-gpu
VERSION=1.0

all:
	@echo "Run 'make install' to install the application."

install:
	install -d $(DESTDIR)$(BINDIR)
	install -m 755 src/main.py $(DESTDIR)$(BINDIR)/$(APPNAME)
	install -d $(DESTDIR)/usr/share/applications
	install -m 644 packaging/$(APPNAME).desktop $(DESTDIR)/usr/share/applications/
	install -d $(DESTDIR)/var/log/$(APPNAME)
	@echo "Installation complete."

uninstall:
	rm -f $(BINDIR)/$(APPNAME)
	rm -f /usr/share/applications/$(APPNAME).desktop
	rm -rf /var/log/$(APPNAME)
	@echo "Uninstallation complete."

rpm:
	mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	tar -czf rpmbuild/SOURCES/$(APPNAME)-$(VERSION).tar.gz --transform "s,^,$(APPNAME)-$(VERSION)/," src packaging	
	rpmbuild -bb --define "_version $(VERSION)" --define "_topdir `pwd`/rpmbuild" packaging/$(APPNAME).spec

clean:
	rm -rf rpmbuild/*

.PHONY: all install uninstall rpm clean