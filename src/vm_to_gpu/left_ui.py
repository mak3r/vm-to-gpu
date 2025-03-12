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
        self.selected_domain = None
        self.create_ui()
        
        # Connect selection change signal
        selection = self.config_treeview.get_selection()
        selection.connect("changed", self.on_selection_changed)

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

    def set_config(self, config):
        """Set the current configuration and refresh UI"""
        self.config = config
        # Refresh the domains by re-reading from virsh and merging with config
        self.domains = self.get_domains()
        # Update the UI with the refreshed domains
        self.load_config_list()
        
    def update(self):
        """Update the left UI based on the shared configuration"""
        # Re-read the domains and refresh the UI
        self.domains = self.get_domains()
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
        # Use the config_manager module for consistency
        from vm_to_gpu.config_manager import load_config
        config = load_config()
        return config.get("domains", [])

    def merge_domains(self, virsh_domains, config_domains):
        """
        Merge domains from virsh and config file:
        - Domains in both: selectable, show config
        - Domains only in virsh: selectable, no config
        - Domains only in config: non-selectable (greyed out), show config
        """
        virsh_domain_names = {domain["name"] for domain in virsh_domains}
        config_domain_names = {domain["name"] for domain in config_domains}
        merged_domains = []

        # Add domains from config_domains
        for domain in config_domains:
            if domain["name"] in virsh_domain_names:
                # Domain is in both config and virsh
                merged_domains.append({
                    "name": domain["name"], 
                    "selectable": True,
                    "configured": True
                })
            else:
                # Domain is only in config (not in virsh)
                merged_domains.append({
                    "name": domain["name"] + " [OFFLINE]", 
                    "selectable": False,
                    "configured": True
                })

        # Add domains from virsh that aren't in config
        for domain in virsh_domains:
            if domain["name"] not in config_domain_names:
                merged_domains.append({
                    "name": domain["name"], 
                    "selectable": True,
                    "configured": False
                })

        return merged_domains

    def on_domain_selected(self, widget, path, column):
        selected_domain = self.config_liststore[path][0]
        # Remove " [OFFLINE]" suffix if present
        clean_domain_name = selected_domain.replace(" [OFFLINE]", "")
        self.selected_domain = clean_domain_name  # Store the clean domain name
        
        # Check if the domain is selectable
        if self.config_liststore[path][1]:
            print(f"Domain selected: {clean_domain_name}")
            
            # Refresh devices first
            self.parent.right_ui.devices = self.parent.right_ui.get_lsusb_devices()
            
            # Check if this domain has configuration
            domain_has_config = False
            if self.config and "domains" in self.config:
                for domain in self.config.get("domains", []):
                    if domain["name"] == clean_domain_name:
                        domain_has_config = True
                        break
            
            if domain_has_config:
                # Apply stored configuration for this domain
                print(f"Applying configuration for domain: {clean_domain_name}")
                self.parent.right_ui.apply_config_for_selected_domain(clean_domain_name)
            else:
                # No config for this domain, reset all devices to not enabled
                print(f"No configuration for domain: {clean_domain_name}")
                # Reset devices and refresh UI
                for device_id in self.parent.right_ui.devices:
                    self.parent.right_ui.devices[device_id]["enabled"] = False
                self.parent.right_ui.load_device_list()
            
    def on_selection_changed(self, selection):
        """
        Called when the selection in the treeview changes
        """
        model, treeiter = selection.get_selected()
        
        if treeiter is not None:
            # Get the domain name from the first column
            domain_name = model[treeiter][0]
            # Remove " [OFFLINE]" suffix if present
            clean_domain = domain_name.replace(" [OFFLINE]", "")
            self.selected_domain = clean_domain
            print(f"Selection changed to: {clean_domain}")
        else:
            self.selected_domain = None
            print("No domain selected")
            
    def get_selected_domain(self):
        """
        Returns the name of the currently selected domain or None if no domain is selected
        """
        if self.selected_domain:
            return self.selected_domain
            
        # Fall back to getting from the selection
        selection = self.config_treeview.get_selection()
        model, treeiter = selection.get_selected()
        
        if treeiter is not None:
            # Get the domain name from the first column and remove any suffix
            domain_name = model[treeiter][0]
            # Remove " [OFFLINE]" suffix if present
            clean_domain = domain_name.replace(" [OFFLINE]", "")
            self.selected_domain = clean_domain
            return clean_domain
        
        return None
        
    def select_domain(self, domain_name):
        """
        Selects a domain by name in the treeview
        """
        if not domain_name:
            return False
            
        # Iterate through the liststore to find the domain
        for i, row in enumerate(self.config_liststore):
            # Check if this is the domain we're looking for (considering [OFFLINE] suffix)
            row_domain = row[0].replace(" [OFFLINE]", "")
            
            if row_domain == domain_name:
                # Select this row
                selection = self.config_treeview.get_selection()
                path = Gtk.TreePath.new_from_indices([i])
                selection.select_path(path)
                self.config_treeview.scroll_to_cell(path, None, True, 0.5, 0.5)
                
                # Update the selected domain
                self.selected_domain = domain_name
                
                # If the domain is selectable, update the right panel
                if row[1]:  # Check selectable flag
                    # First refresh the device list from lsusb
                    self.parent.right_ui.devices = self.parent.right_ui.get_lsusb_devices()
                    
                    # Check if this domain has configuration
                    domain_has_config = False
                    if self.config and "domains" in self.config:
                        for domain in self.config.get("domains", []):
                            if domain["name"] == domain_name:
                                domain_has_config = True
                                break
                    
                    if domain_has_config:
                        # Apply stored configuration for this domain
                        print(f"Applying configuration for domain: {domain_name}")
                        self.parent.right_ui.apply_config_for_selected_domain(domain_name)
                    else:
                        # No config for this domain, reset all devices to not enabled
                        print(f"No configuration for domain: {domain_name}")
                        # Reset devices and refresh UI
                        for device_id in self.parent.right_ui.devices:
                            self.parent.right_ui.devices[device_id]["enabled"] = False
                        self.parent.right_ui.load_device_list()
                
                return True
                
        return False

    