from pathlib import Path

from ferris_layer.hidraw_interface import HidrawInterface


class HidrawFinder:
    def __init__(self, sysfs, vendor_id, product_id):
        self._sysfs = Path(sysfs)
        self._vendor_id = vendor_id
        self._product_id = product_id

    def find(self):
        for interface in self._interfaces():
            if self._is_keyboard_raw_hid(interface):
                return interface.device_path()

        return None

    def _interfaces(self):
        return (HidrawInterface(entry) for entry in sorted(self._sysfs.iterdir()))

    def _is_keyboard_raw_hid(self, interface):
        return interface.belongs_to(self._vendor_id, self._product_id) and interface.is_raw_hid()
