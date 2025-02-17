# buttons.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Buttons(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.app = app
        self.create_ui()

    def create_ui(self):
        # Add buttons
        btn_refresh = Gtk.Button(label="Refresh USB Devices")
        btn_refresh.connect("clicked", self.on_refresh_devices)
        self.pack_start(btn_refresh, True, True, 0)

        btn_save = Gtk.Button(label="Save Configuration")
        btn_save.connect("clicked", self.on_save_configuration)
        self.pack_start(btn_save, True, True, 0)

        btn_attach = Gtk.Button(label="Attach & Start VM")
        btn_attach.connect("clicked", self.on_attach_start_vm)
        self.pack_start(btn_attach, True, True, 0)

        btn_detach = Gtk.Button(label="Detach & Stop VM")
        btn_detach.connect("clicked", self.on_detach_stop_vm)
        self.pack_start(btn_detach, True, True, 0)

    def on_refresh_devices(self, widget):
        # Handle button click event
        self.app.refresh_devices()

    def on_save_configuration(self, widget):
        # Handle button click event
        self.app.save_configuration()

    def on_attach_start_vm(self, widget):
        # Handle button click event
        self.app.attach_start_vm()

    def on_detach_stop_vm(self, widget):
        # Handle button click event
        self.app.detach_stop_vm()