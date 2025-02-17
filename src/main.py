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
        self.devices = self.get_lsusb_devices()

        self.create_ui()

        # Connect the configure-event signal to the handler
        self.connect("configure-event", self.on_configure_event)


    def create_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=self.spacing)
        self.add(main_box)

        # Create a horizontal box to hold the left and right panels
        panels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.spacing)
        main_box.pack_start(panels_box, True, True, 0)

        self.left_ui = LeftUI(self)
        self.right_ui = RightUI()
        self.buttons = Buttons(self)

        self.left_ui.set_width(int(self.get_size()[0] * .3))
        self.right_ui.set_width(int(self.get_size()[0] *.7))

        panels_box.pack_start(self.left_ui, True, True, 0)
        panels_box.pack_start(self.right_ui, True, True, 0)

        main_box.pack_start(self.buttons, False, False, 0)

        # Set the width of the LeftUI to 30% of the total available horizontal space
        print(self.get_size())

    def load_config(self):
        # Load configuration
        return {}

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
            self.left_ui.update(self.config)
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


if __name__ == "__main__":
    app = VMToGPUApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()