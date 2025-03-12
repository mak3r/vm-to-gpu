#!/usr/bin/env python3

import sys
import os

# Add the directory containing the Python modules to the Python path
sys.path.append('/usr/local/lib/python3.x/site-packages')

# main.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from vm_to_gpu.left_ui import LeftUI
from vm_to_gpu.right_ui import RightUI
from vm_to_gpu.buttons import Buttons


class VMToGPUApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="VM to GPU Manager")
        self.curw = 1000
        self.curh = 640
        self.spacing = 6
        self.set_default_size(self.curw, self.curh)

        self.config = self.load_config()
        # We'll get devices from the right_ui after it's created

        self.create_ui()
        
        # Initialize both UI panels with the loaded configuration
        self.right_ui.set_config(self.config)  # Initialize right panel first
        self.left_ui.set_config(self.config)   # Then left panel
        
        # If there are domains in the configuration, try to select the first one
        if self.config and "domains" in self.config and self.config["domains"]:
            first_domain = self.config["domains"][0]["name"]
            print(f"Auto-selecting first domain with config: {first_domain}")
            self.left_ui.select_domain(first_domain)
        # Otherwise select first domain from virsh if available
        elif hasattr(self.left_ui, "domains") and self.left_ui.domains:
            first_virsh_domain = self.left_ui.domains[0]["name"]
            print(f"Auto-selecting first available domain: {first_virsh_domain}")
            self.left_ui.select_domain(first_virsh_domain)

        # Connect the configure-event signal to the handler
        self.connect("configure-event", self.on_configure_event)


    def create_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=self.spacing)
        self.add(main_box)

        # Create a horizontal box to hold the left and right panels
        panels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.spacing)
        main_box.pack_start(panels_box, True, True, 0)

        self.left_ui = LeftUI(self)
        self.right_ui = RightUI(self)
        self.buttons = Buttons(self)

        self.left_ui.set_width(int(self.get_size()[0] * .3))
        self.right_ui.set_width(int(self.get_size()[0] *.7))

        panels_box.pack_start(self.left_ui, True, True, 0)
        panels_box.pack_start(self.right_ui, True, True, 0)

        main_box.pack_start(self.buttons, False, False, 0)

        # Set the width of the LeftUI to 30% of the total available horizontal space
        print(self.get_size())

    def load_config(self):
        # Load configuration using the config_manager
        from vm_to_gpu.config_manager import load_config
        return load_config()

    def get_lsusb_devices(self):
        # Get USB devices
        return []

    def refresh(self):
        # Get the current size of the window
        ui_width, ui_height = self.get_size()[0]-self.spacing, self.get_size()[1]

        if self.curw != ui_width:
            # Set the width of the LeftUI to 30% of the total available horizontal space
            left_ui_width = int(ui_width * 0.3)
            right_ui_width = ui_width - left_ui_width

            self.left_ui.set_width(left_ui_width)
            self.right_ui.set_width(right_ui_width)

            # Refresh the UI components
            self.left_ui.update()
            self.right_ui.update(self.config)

            self.curw = ui_width
            self.curh = ui_height

    def on_configure_event(self, widget, event):
        # Call the refresh method when the window is resized
        self.refresh()

    def refresh_devices(self):
        # Implement the logic to refresh devices
        print("Refreshing devices...")
        self.right_ui.devices = self.right_ui.get_lsusb_devices()
        self.right_ui.load_device_list()
        
    def save_configuration(self):
        """
        Save the current configuration for the selected domain with selected devices
        """
        from vm_to_gpu.config_manager import load_config, save_config, create_domain, add_device_to_domain
        
        print("Saving configuration...")
        
        # Get the currently selected domain from the left panel
        selected_domain = self.left_ui.get_selected_domain()
        if not selected_domain:
            print("No domain selected. Cannot save configuration.")
            # Display an error dialog
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text="No domain selected"
            )
            dialog.format_secondary_text(
                "Please select a VM domain before saving configuration."
            )
            dialog.run()
            dialog.destroy()
            return
            
        # Get the selected devices from the right panel
        selected_devices = self.right_ui.get_selected_devices()
        
        # Load the current configuration
        config = load_config()
        
        # Clean the domain name (remove any suffix like " [OFFLINE]")
        clean_domain_name = selected_domain.replace(" [OFFLINE]", "")
        
        # Find if the domain already exists in the config
        domain_exists = False
        domain_index = -1
        
        for i, domain in enumerate(config.get("domains", [])):
            if domain["name"] == clean_domain_name:
                domain_exists = True
                domain_index = i
                break
                
        # If domain doesn't exist, create it
        if not domain_exists:
            # Create a new domain entry
            new_domain = {
                "name": clean_domain_name,
                "devices": []
            }
            config["domains"].append(new_domain)
            domain_index = len(config["domains"]) - 1
            
        # Clear existing devices for this domain
        config["domains"][domain_index]["devices"] = []
        
        # Add selected devices to the domain
        for device in selected_devices:
            device_info = {
                "vendor": device["vendor_name"],
                "product": device["product_name"],
                "vendor0x": device["vendor0x"],
                "product0x": device["product0x"],
                "enabled": True
            }
            config["domains"][domain_index]["devices"].append(device_info)
            
        # Save the updated configuration
        save_config(config)
        
        # Confirm to the user
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Configuration Saved"
        )
        dialog.format_secondary_text(
            f"Configuration for {clean_domain_name} has been saved with {len(selected_devices)} device(s)."
        )
        dialog.run()
        dialog.destroy()
        
        # Refresh the UI to reflect the changes
        self.config = config
        
        print(f"Configuration saved for domain: {clean_domain_name}")
        
        # Update the left UI first
        self.left_ui.set_config(self.config)
        
        # Make sure the domain stays selected
        self.left_ui.select_domain(clean_domain_name)


if __name__ == "__main__":
    app = VMToGPUApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()