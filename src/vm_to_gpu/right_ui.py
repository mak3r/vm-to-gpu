# right_ui.py
import gi
import subprocess
import pprint

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class RightUI(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.devices = self.get_lsusb_devices()
        # self.dump_devices()
        self.create_ui()

    def create_ui(self):
        # Right pane - Device list
        # Initialize the TreeStore
        self.device_treestore = Gtk.TreeStore(str, str, bool)
        # Create a TreeView
        self.treeview = Gtk.TreeView(model=self.device_treestore)

        # Create columns for the TreeView
        # Column for Vendor Name or Product Name
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Vendor Name", renderer_text, text=0)
        self.treeview.append_column(column_text)

        # Column for Device ID (only for products, not vendors)
        renderer_device_id = Gtk.CellRendererText()
        column_device_id = Gtk.TreeViewColumn("Device ID", renderer_device_id, text=1)
        self.treeview.append_column(column_device_id)

        # Column for Enabled Checkbox
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_toggle_device)
        column_toggle = Gtk.TreeViewColumn("Enabled", renderer_toggle, active=2)
        self.treeview.append_column(column_toggle)

        self.load_device_list()

        device_scroll = Gtk.ScrolledWindow()
        device_scroll.add(self.treeview)
        self.pack_start(device_scroll, True, True, 0)

    def get_lsusb_devices(self):
        result = subprocess.run(["lsusb", "-v"], capture_output=True, text=True)
        devices = {}
        for line in result.stdout.splitlines():
            parts = line.split()
            if "Bus" in parts:
                # Create a new device record
                bus_index = parts.index("Bus")
                device_index = parts.index("Device")
                id_index = parts.index("ID")
                # Ensure device_id is a string
                device_id = f"{parts[bus_index + 1]}:{parts[bus_index + 3]}:{parts[bus_index + 5]}"
                devices[device_id] = {
                     "vendor0x": "n/a",
                     "vendor_name": "n/a",
                     "product0x": "n/a",
                     "product_name": "n/a",
                     "enabled": False
                }
            if "idVendor" in parts:
                vendor_index = parts.index("idVendor")
                devices[device_id]["vendor0x"] = " ".join(parts[vendor_index + 1])
                devices[device_id]["vendor_name"] = " ".join(parts[vendor_index + 2:])
            if "idProduct" in parts:
                product_index = parts.index("idProduct")
                devices[device_id]["product0x"] = parts[product_index + 1]
                devices[device_id]["product_name"] = " ".join(parts[product_index + 2:])
        
        return devices

    def load_device_list(self):
        self.device_treestore.clear()

        # Group devices by vendor_name
        grouped_devices = {}
        for device in self.devices:
            vendor_name = self.devices[device]["vendor_name"]
            if vendor_name not in grouped_devices:
                grouped_devices[vendor_name] = []
            grouped_devices[vendor_name].append(device)

        # Sort the vendors by name
        sorted_vendors = sorted(grouped_devices.keys())

        # Append data to the TreeStore
        for vendor_name in sorted_vendors:
            vendor_iter = self.device_treestore.append(None, [vendor_name, "", False])
            for device in grouped_devices[vendor_name]:
                self.device_treestore.append(vendor_iter, [self.devices[device]["product_name"], "", self.devices[device]["enabled"]])

    def on_toggle_device(self, widget, path):
        self.device_treestore[path][2] = not self.device_treestore[path][2]

    def update(self, config):
        # Update the right UI based on the shared configuration
        pass

    def set_width(self, width):
        self.set_size_request(width, -1)

    def dump_devices(self):
        pprint.pprint(self.devices)