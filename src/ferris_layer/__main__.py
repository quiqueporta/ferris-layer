import os
import threading
import time
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ferris_layer.config import load_layer_names
from ferris_layer.displays import Displays
from ferris_layer.ferris_sweep import PRODUCT_ID, VENDOR_ID
from ferris_layer.hidraw_device import HidrawDevice
from ferris_layer.hidraw_finder import HidrawFinder
from ferris_layer.hidraw_keyboard import HidrawKeyboard
from ferris_layer.keyboard_connection import KeyboardConnection
from ferris_layer.layer_icons import LayerIcons
from ferris_layer.layer_watcher import LayerWatcher
from ferris_layer.layout_window import LayoutWindow, MainLoopDisplay
from ferris_layer.live_layout import LiveLayout
from ferris_layer.tray_indicator_display import TrayIndicatorDisplay


RETRY_SECONDS = 2
CONFIG_PATH = Path.home() / ".config" / "ferris-layer" / "config.toml"


def main():
    finder = HidrawFinder("/sys/class/hidraw", VENDOR_ID, PRODUCT_ID)
    names = load_layer_names(CONFIG_PATH)
    live_layout = _live_layout(finder, names)
    tray = TrayIndicatorDisplay(icons=LayerIcons(_icons_directory()), show_layout=live_layout.open)
    connection = KeyboardConnection(
        finder=finder,
        open_keyboard=HidrawKeyboard,
        watcher=LayerWatcher(display=Displays(tray, MainLoopDisplay(live_layout)), names=names),
        wait=lambda: time.sleep(RETRY_SECONDS),
    )

    threading.Thread(target=_keep_watching, args=(connection,), daemon=True).start()
    Gtk.main()


def _live_layout(finder, names):
    window = LayoutWindow()
    live_layout = LiveLayout(finder=finder, open_keyboard=HidrawDevice, window=window, names=names)

    window.when_closed(live_layout.close)

    return live_layout


def _icons_directory():
    directory = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "ferris-layer"
    directory.mkdir(exist_ok=True)

    return directory


def _keep_watching(connection):
    while True:
        connection.run_once()


if __name__ == "__main__":
    main()
