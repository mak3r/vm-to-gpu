# left_ui.py
import json
import os
import pprint
import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class LeftUI(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.domains = self.get_domains()
        self.parent = parent
        self.config = self.parent.config
        self.create_ui()

    def create_ui(self):
        # When we first create the UI, we need to load the list of domains
        # from the config file and display those domains in the liststore
        # Then we need to get the list of domains from the subcommand
        # 'virsh list --all' and display those domains in the liststore
        # Domains from the config file should be displayed in red if they
        # are not in the virsh command output
        self.config_liststore = Gtk.ListStore(str, bool)
        self.config_treeview = Gtk.TreeView(model=self.config_liststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Configurations", renderer, text=0)
        column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)  # Auto-size column
        column.set_resizable(True)  # Allow resizing
        column.set_min_width(100)  # Set minimum width
        self.config_treeview.append_column(column)

        self.load_config_list()

        config_scroll = Gtk.ScrolledWindow()
        config_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        config_scroll.set_min_content_height(200)  # Set minimum height
        config_scroll.add(self.config_treeview)
        self.pack_start(config_scroll, True, True, 0)  # Allow expansion

        self.config_treeview.connect("row-activated", self.on_domain_selected)
        # Make sure TreeView is visible
        self.config_treeview.show_all()

    def load_config_list(self):
        self.config_liststore.clear()
        for domain in self.domains:
            self.config_liststore.append([domain["name"], domain["selectable"]])

    def update(self):
        # Update the left UI based on the shared configuration
        self.load_config_list()

    def set_width(self, width):
        self.set_size_request(width, -1)

    def get_domains(self):
        print("Getting domains")
        # Get domains from virsh
        virsh_domains = self.get_virsh_domains()

        # Get domains from config file
        config_domains = self.get_config_domains()

        # Merge domains
        merged_domains = self.merge_domains(virsh_domains, config_domains)

        return merged_domains

    def get_virsh_domains(self):
        result = subprocess.run(["sudo", "virsh", "list", "--all"], capture_output=True, text=True)
        domains = []
        lines = result.stdout.splitlines()
        
        for line in lines[2:]:  # Skip the header lines
            parts = line.split()
            
            # Make sure we have at least two parts (ID and name)
            if parts and len(parts) >= 2:
                if parts[0].isdigit():
                    print("Domain: ", parts[1], " is running")
                elif parts[0] == "-":
                    print("Domain: ", parts[1], " is not running")
                # Add domain regardless of state (running or not)
                domains.append({"name": parts[1], "selectable": True})

        return domains

    def get_config_domains(self):
        config_file = os.path.expanduser("~/.config/vm_to_gpu/config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config = json.load(file)
                return config.get("domains", [])
        return []

    def merge_domains(self, virsh_domains, config_domains):
        virsh_domain_names = {domain["name"] for domain in virsh_domains}
        merged_domains = []

        for domain in config_domains:
            if domain["name"] in virsh_domain_names:
                merged_domains.append({"name": domain["name"], "selectable": True})
            else:
                merged_domains.append({"name": domain["name"], "selectable": False})

        for domain in virsh_domains:
            if domain["name"] not in [d["name"] for d in merged_domains]:
                merged_domains.append({"name": domain["name"], "selectable": True})

        return merged_domains

    def on_domain_selected(self, widget, path, column):
        selected_domain = self.config_liststore[path][0]
        if self.config_liststore[path][1]:  # Check if the domain is selectable
            self.parent.right_ui.devices = self.parent.right_ui.get_lsusb_devices()
            self.parent.right_ui.load_device_list()
            self.parent.right_ui.update(self.config)

    