import json
import sys
from pathlib import Path

from ferris_layer.ferris_sweep import MATRIX_COLS, MATRIX_ROWS, PRODUCT_ID, VENDOR_ID
from ferris_layer.hidraw_device import HidrawDevice
from ferris_layer.hidraw_finder import HidrawFinder
from ferris_layer.keymap_source import KeymapSource
from ferris_layer.layer_images import LayerImages
from ferris_layer.via_backup import ViaBackup


USAGE = "Usage: ferris-via-backup save|restore|keymap <backup.json> | images <backup.json> <directory>"
ARGUMENT_COUNTS = {"save": 1, "restore": 1, "keymap": 1, "images": 2}


def main(argv=None):
    action, path, *directory = _arguments(sys.argv[1:] if argv is None else argv)

    if action == "images":
        LayerImages(MATRIX_ROWS, MATRIX_COLS, *directory).write(_read(path))
    elif action == "keymap":
        print(KeymapSource(MATRIX_ROWS, MATRIX_COLS).render(_read(path)), end="")
    elif action == "save":
        path.write_text(json.dumps(_with_keyboard(_backup().save), indent=2) + "\n")
        print(f"Backup saved to {path}")
    else:
        _with_keyboard(lambda keyboard: _backup().restore(keyboard, _read(path)))
        print(f"Backup restored from {path}")


def _arguments(argv):
    if not argv or len(argv) - 1 != ARGUMENT_COUNTS.get(argv[0]):
        sys.exit(USAGE)

    return argv[0], *(Path(argument) for argument in argv[1:])


def _backup():
    return ViaBackup(matrix_keys=MATRIX_ROWS * MATRIX_COLS)


def _read(path):
    return json.loads(path.read_text())


def _with_keyboard(action):
    keyboard = HidrawDevice(_keyboard_path())
    try:
        return action(keyboard)
    finally:
        keyboard.close()


def _keyboard_path():
    path = HidrawFinder("/sys/class/hidraw", VENDOR_ID, PRODUCT_ID).find()
    if path is None:
        sys.exit("Ferris Sweep not found. Is it plugged in and is the udev rule installed?")

    return path


if __name__ == "__main__":
    main()
