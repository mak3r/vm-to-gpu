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
        button = Gtk.Button(label="Refresh")
        button.connect("clicked", self.on_refresh_clicked)
        self.pack_start(button, True, True, 0)

    def on_refresh_clicked(self, widget):
        # Handle button click event
        self.app.refresh()