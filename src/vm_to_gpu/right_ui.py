# right_ui.py
import gi
import subprocess
import pprint

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class RightUI(Gtk.Box):
    def __init__(self, parent=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.parent = parent
        self.devices = self.get_lsusb_devices()
        self.config = {}  # Initialize empty config
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
                devices[device_id]["vendor0x"] = parts[vendor_index + 1]  # Direct assignment, no join
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
        for device_id, device in self.devices.items():
            vendor_name = device["vendor_name"]
            if vendor_name not in grouped_devices:
                grouped_devices[vendor_name] = []
            grouped_devices[vendor_name].append(device_id)

        # Sort the vendors by name
        sorted_vendors = sorted(grouped_devices.keys())

        # Append data to the TreeStore
        for vendor_name in sorted_vendors:
            # Check if all devices for this vendor are enabled
            all_devices_enabled = all(self.devices[device_id]["enabled"] for device_id in grouped_devices[vendor_name])
            
            # Create the vendor node with enabled state based on children
            vendor_iter = self.device_treestore.append(None, [vendor_name, "", all_devices_enabled])
            
            # Add the devices for this vendor
            for device_id in grouped_devices[vendor_name]:
                device = self.devices[device_id]
                # Add product ID to display
                product_id_display = device["product0x"]
                
                # Check if this is a ghost device (configured but not currently present)
                is_ghost = device.get("ghost", False)
                
                # Create display text with greyed-out indicator if needed
                product_name = device["product_name"]
                if is_ghost:
                    product_name = f"[UNAVAILABLE] {product_name}"
                
                # Add to the treestore with product name, ID, and enabled state
                self.device_treestore.append(vendor_iter, [product_name, product_id_display, device["enabled"]])

    def on_toggle_device(self, widget, path_str):
        # In GTK3, the path parameter is already a string like "0" or "0:1"
        # Toggle the selected state of the device
        new_state = not self.device_treestore[path_str][2]
        self.device_treestore[path_str][2] = new_state
        
        # Convert string path to TreeIter
        treeiter = self.device_treestore.get_iter_from_string(path_str)
        
        # If it's a vendor (parent) node, toggle all its children
        if self.device_treestore.iter_has_child(treeiter):
            child_iter = self.device_treestore.iter_children(treeiter)
            while child_iter:
                child_path = self.device_treestore.get_path(child_iter)
                child_path_str = str(child_path)
                self.device_treestore[child_path_str][2] = new_state
                child_iter = self.device_treestore.iter_next(child_iter)
        
        # If it's a child node, check if we need to update parent state
        elif ":" in path_str:  # Child nodes have a path like "0:1" (second child of first parent)
            # Extract parent path
            parent_path_str = path_str.split(":")[0]
            parent_iter = self.device_treestore.get_iter_from_string(parent_path_str)
            
            # Check all siblings
            all_enabled = True
            any_enabled = False
            
            child_iter = self.device_treestore.iter_children(parent_iter)
            while child_iter:
                child_path = self.device_treestore.get_path(child_iter)
                child_path_str = str(child_path)
                if self.device_treestore[child_path_str][2]:
                    any_enabled = True
                else:
                    all_enabled = False
                child_iter = self.device_treestore.iter_next(child_iter)
            
            # Set parent state based on children
            # If all children are enabled, parent is enabled
            # If no children are enabled, parent is disabled
            if all_enabled:
                self.device_treestore[parent_path_str][2] = True
            elif not any_enabled:
                self.device_treestore[parent_path_str][2] = False
                
        # Update our internal device list to match the UI
        self.update_devices_from_treestore()

    def update_devices_from_treestore(self):
        """
        Update internal devices dictionary based on the treestore selections
        """
        # Create a mapping from product name to device ID
        product_to_device = {}
        for device_id, device in self.devices.items():
            clean_name = device["product_name"]
            # Remove the [UNAVAILABLE] prefix if present
            if "[UNAVAILABLE]" in clean_name:
                clean_name = clean_name.replace("[UNAVAILABLE] ", "")
            product_to_device.setdefault(clean_name, []).append(device_id)
            
        # Iterate through the treestore
        def process_node(treeiter, parent_iter=None):
            while treeiter:
                product_name = self.device_treestore[treeiter][0]
                is_enabled = self.device_treestore[treeiter][2]
                
                # Clean the product name (remove any [UNAVAILABLE] prefix)
                clean_product_name = product_name
                if "[UNAVAILABLE]" in clean_product_name:
                    clean_product_name = clean_product_name.replace("[UNAVAILABLE] ", "")
                
                # If it's a product node (child node)
                if parent_iter is not None:
                    # Find matching devices and update their enabled state
                    if clean_product_name in product_to_device:
                        for device_id in product_to_device[clean_product_name]:
                            self.devices[device_id]["enabled"] = is_enabled
                
                # Process children if any
                if self.device_treestore.iter_has_child(treeiter):
                    child_iter = self.device_treestore.iter_children(treeiter)
                    process_node(child_iter, treeiter)
                
                # Move to next sibling
                treeiter = self.device_treestore.iter_next(treeiter)
                
        # Start with root level nodes
        root_iter = self.device_treestore.get_iter_first()
        process_node(root_iter)

    def get_selected_devices(self):
        """
        Return a list of selected devices
        """
        selected_devices = []
        for device_id, device in self.devices.items():
            if device["enabled"]:
                device_info = device.copy()
                device_info["id"] = device_id
                selected_devices.append(device_info)
        return selected_devices

    def set_config(self, config):
        """Set the current configuration and refresh UI"""
        self.config = config
        # Apply the configuration based on the currently selected domain
        self.apply_config_for_selected_domain()
        
    def apply_config_for_selected_domain(self, domain_name=None):
        """
        Apply configuration for the specified domain or currently selected domain
        
        Args:
            domain_name: Optional specific domain name to apply config for
        """
        # If no domain was specified, get the selected domain from the left panel
        selected_domain = domain_name
        if selected_domain is None and hasattr(self, "parent") and hasattr(self.parent, "left_ui"):
            selected_domain = self.parent.left_ui.get_selected_domain()
            
        print(f"Applying config for domain: {selected_domain}")
        
        if not selected_domain or not self.config or "domains" not in self.config:
            # If no domain is selected or no config, just load devices without enabling any
            self.load_device_list()
            return
            
        # Find the configuration for the selected domain
        domain_config = None
        for domain in self.config.get("domains", []):
            if domain["name"] == selected_domain:
                domain_config = domain
                break
                
        if not domain_config or "devices" not in domain_config:
            # If no config for this domain, reset all devices to not enabled
            print(f"No configuration found for domain: {selected_domain}")
            for device_id in self.devices:
                self.devices[device_id]["enabled"] = False
            self.load_device_list()
            return
            
        # Reset all devices to not enabled
        for device_id in self.devices:
            self.devices[device_id]["enabled"] = False
            
        # Mark devices as enabled based on the config
        for device_config in domain_config.get("devices", []):
            # Try to match by vendor and product IDs
            match_found = False
            for device_id, device in self.devices.items():
                if (device["vendor0x"] == device_config.get("vendor0x") and
                    device["product0x"] == device_config.get("product0x")):
                    device["enabled"] = True
                    match_found = True
                    break
            
            # If no match was found, add the device as "ghost" (not available but in config)
            if not match_found:
                # Create a unique ID for this ghost device
                ghost_id = f"ghost:{device_config.get('vendor0x')}:{device_config.get('product0x')}"
                # Add it to our devices dict with a flag indicating it's not actually present
                self.devices[ghost_id] = {
                    "vendor0x": device_config.get("vendor0x"),
                    "vendor_name": device_config.get("vendor", "Unknown Vendor"),
                    "product0x": device_config.get("product0x"),
                    "product_name": device_config.get("product", "Unavailable Device"),
                    "enabled": True,
                    "ghost": True  # Flag to indicate this device is not actually present
                }
                    
        # Reload the device list to reflect the changes
        self.load_device_list()
        
    def update(self, config):
        """Update the UI to reflect the configuration"""
        self.config = config
        
        # Get the current selected domain
        selected_domain = None
        if hasattr(self, "parent") and hasattr(self.parent, "left_ui"):
            selected_domain = self.parent.left_ui.get_selected_domain()
            
        # Update our device list from lsusb
        self.devices = self.get_lsusb_devices()
        
        # Apply the configuration for the selected domain
        self.apply_config_for_selected_domain(selected_domain)

    def set_width(self, width):
        self.set_size_request(width, -1)

    def dump_devices(self):
        pprint.pprint(self.devices)