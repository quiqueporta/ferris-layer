import os
import threading
import time
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ferris_layer.config import load_layer_names
from ferris_layer.hidraw_finder import HidrawFinder
from ferris_layer.hidraw_keyboard import HidrawKeyboard
from ferris_layer.keyboard_connection import KeyboardConnection
from ferris_layer.layer_icons import LayerIcons
from ferris_layer.layer_watcher import LayerWatcher
from ferris_layer.tray_indicator_display import TrayIndicatorDisplay


FERRIS_VENDOR_ID = 0xC2AB
FERRIS_PRODUCT_ID = 0x3939
RETRY_SECONDS = 2
CONFIG_PATH = Path.home() / ".config" / "ferris-layer" / "config.toml"


def main():
    display = TrayIndicatorDisplay(icons=LayerIcons(_icons_directory()))
    connection = KeyboardConnection(
        finder=HidrawFinder("/sys/class/hidraw", FERRIS_VENDOR_ID, FERRIS_PRODUCT_ID),
        open_keyboard=HidrawKeyboard,
        watcher=LayerWatcher(display=display, names=load_layer_names(CONFIG_PATH)),
        wait=lambda: time.sleep(RETRY_SECONDS),
    )

    threading.Thread(target=_keep_watching, args=(connection,), daemon=True).start()
    Gtk.main()


def _icons_directory():
    directory = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "ferris-layer"
    directory.mkdir(exist_ok=True)

    return directory


def _keep_watching(connection):
    while True:
        connection.run_once()


if __name__ == "__main__":
    main()
