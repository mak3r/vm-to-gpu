# left_ui.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class LeftUI(Gtk.Box):
    def __init__(self, parent):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.create_ui()
        self.parent = parent
        self.config = self.parent.config

    def create_ui(self):
        self.config_liststore = Gtk.ListStore(str)
        self.config_treeview = Gtk.TreeView(model=self.config_liststore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Configurations", renderer, text=0)
        self.config_treeview.append_column(column)

        # self.load_config_list()

        config_scroll = Gtk.ScrolledWindow()
        config_scroll.set_size_request(200, -1)
        config_scroll.add(self.config_treeview)
        self.pack_start(config_scroll, False, False, 0)
        
        # Add widgets for the left UI
        # label = Gtk.Label(label="Left UI")
        # self.pack_start(label, True, True, 0)

    def load_config_list(self):
        self.config_liststore.clear()
        for system in self.config.get("systems", []):
            self.config_liststore.append([system["name"]])
            
    def update(self, config):
        # Update the left UI based on the shared configuration
        pass
    
    def set_width(self, width):
        self.set_size_request(width, -1)