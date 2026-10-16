import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import AyatanaAppIndicator3 as AppIndicator
from gi.repository import GLib, Gtk


INDICATOR_ID = "ferris-layer"


class TrayIndicatorDisplay:
    def __init__(self, icons, show_layout):
        self._icons = icons
        self._show_layout = show_layout
        self._layer_item = Gtk.MenuItem(label="")
        self._indicator = AppIndicator.Indicator.new(
            INDICATOR_ID, "input-keyboard", AppIndicator.IndicatorCategory.HARDWARE
        )

        self._indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self._indicator.set_menu(self._menu())

    def show(self, layer):
        GLib.idle_add(self._present, layer)

    def _present(self, layer):
        description = layer.description()

        self._indicator.set_icon_full(self._icons.icon_for(layer), description)
        self._indicator.set_title(description)
        self._layer_item.set_label(description)

        return False

    def _menu(self):
        menu = Gtk.Menu()
        layout_item = Gtk.MenuItem(label="Show layout")
        layout_item.connect("activate", lambda _item: self._show_layout())
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda _item: Gtk.main_quit())

        self._layer_item.set_sensitive(False)
        menu.append(self._layer_item)
        menu.append(layout_item)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(quit_item)
        menu.show_all()

        return menu
