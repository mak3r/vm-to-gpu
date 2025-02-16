#!/usr/bin/env python3

import json
import subprocess
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

CONFIG_FILE = "config.json"

class VMToGPUApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="VM to GPU Manager")
        self.set_default_size(600, 400)

        self.config = self.load_config()
        self.devices = self.get_lsusb_devices()

        self.create_ui()

    def create_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        # Left pane - Configuration list
        self.config_liststore = Gtk.ListStore(str)
        self.config_treeview = Gtk.TreeView(model=self.config_liststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Configurations", renderer, text=0)
        self.config_treeview.append_column(column)

        self.load_config_list()

        config_scroll = Gtk.ScrolledWindow()
        config_scroll.set_size_request(200, -1)
        config_scroll.add(self.config_treeview)
        hbox.pack_start(config_scroll, False, False, 0)

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
        hbox.pack_start(device_scroll, True, True, 0)

        # Buttons
        button_box = Gtk.Box(spacing=6)
        vbox.pack_start(button_box, False, False, 0)

        btn_refresh = Gtk.Button(label="Refresh USB Devices")
        btn_refresh.connect("clicked", self.on_refresh_devices)
        button_box.pack_start(btn_refresh, True, True, 0)

        btn_save = Gtk.Button(label="Save Configuration")
        btn_save.connect("clicked", self.on_save_configuration)
        button_box.pack_start(btn_save, True, True, 0)

        btn_attach = Gtk.Button(label="Attach & Start VM")
        btn_attach.connect("clicked", self.on_attach_start_vm)
        button_box.pack_start(btn_attach, True, True, 0)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"systems": []}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

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

    def load_config_list(self):
        self.config_liststore.clear()
        for system in self.config.get("systems", []):
            self.config_liststore.append([system["name"]])

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

    def on_refresh_devices(self, widget):
        self.devices = self.get_lsusb_devices()
        self.load_device_list()

    def on_save_configuration(self, widget):
        # Implement saving logic to JSON
        print("Saving configuration...")
        self.save_config()

    def on_attach_start_vm(self, widget):
        # Implement attach devices & start VM logic
        print("Attaching devices and starting VM...")

if __name__ == "__main__":
    app = VMToGPUApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
    Gtk.main()