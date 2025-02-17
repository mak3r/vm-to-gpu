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
        self.set_default_size(800, 640)

        self.config = self.load_config()
        self.devices = self.get_lsusb_devices()

        self.create_ui()

    def create_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(main_box)

        # Create a horizontal box to hold the left and right panels
        panels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        main_box.pack_start(panels_box, True, True, 0)

        self.left_ui = LeftUI(self)
        self.right_ui = RightUI()
        self.buttons = Buttons(self)

        panels_box.pack_start(self.left_ui, True, True, 0)
        panels_box.pack_start(self.right_ui, True, True, 0)

        main_box.pack_start(self.buttons, False, False, 0)

        # Set the width of the LeftUI to 30% of the total available horizontal space
        #print(self.get_size()[0])
        #self.left_ui.set_width(int(self.get_size()[0] / .25))
        self.left_ui.set_width(100)


    def load_config(self):
        # Load configuration
        return {}

    def get_lsusb_devices(self):
        # Get USB devices
        return []

    def refresh(self):
        # Refresh the UI components
        self.left_ui.update(self.config)
        self.right_ui.update(self.config)

if __name__ == "__main__":
    app = VMToGPUApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()