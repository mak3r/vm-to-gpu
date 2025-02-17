# right_ui.py
import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class RightUI(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.devices = self.get_lsusb_devices()
        self.create_ui()

    def create_ui(self):
        # Right pane - Device list
        self.device_liststore = Gtk.ListStore(str, str, str, bool)
        self.device_treeview = Gtk.TreeView(model=self.device_liststore)

        renderer_text = Gtk.CellRendererText()
        column_vendor = Gtk.TreeViewColumn("Vendor", renderer_text, text=0)
        self.device_treeview.append_column(column_vendor)

        column_product = Gtk.TreeViewColumn("Product", renderer_text, text=1)
        self.device_treeview.append_column(column_product)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggle_device)
        column_enabled = Gtk.TreeViewColumn("Enabled", renderer_toggle, active=3)
        self.device_treeview.append_column(column_enabled)

        self.load_device_list()

        device_scroll = Gtk.ScrolledWindow()
        device_scroll.add(self.device_treeview)
        self.pack_start(device_scroll, True, True, 0)
        
        # Add widgets for the right UI
        # label = Gtk.Label(label="Right UI")
        # self.pack_start(label, True, True, 0)

    def get_lsusb_devices(self):
        result = subprocess.run(["lsusb"], capture_output=True, text=True)
        devices = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if "ID" in parts:
                id_index = parts.index("ID")
                vendor0x, product0x = parts[id_index + 1].split(":")
                vendor_name = " ".join(parts[id_index + 2:])
                product_name = parts[-1]
                devices.append({
                    "vendor0x": vendor0x,
                    "vendor id": vendor_name,
                    "product0x": product0x,
                    "product": product_name,
                    "enabled": False
                })
        return devices

    def load_device_list(self):
        self.device_liststore.clear()
        for device in self.devices:
            self.device_liststore.append([
                device["vendor id"],
                device["product"],
                device["product0x"],
                device["enabled"]
            ])

    def on_toggle_device(self, widget, path):
        self.device_liststore[path][3] = not self.device_liststore[path][3]

    def update(self, config):
        # Update the right UI based on the shared configuration
        pass