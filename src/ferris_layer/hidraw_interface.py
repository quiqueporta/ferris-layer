RAW_HID_USAGE_PAGE = bytes([0x06, 0x60, 0xFF])


class HidrawInterface:
    def __init__(self, sysfs_entry):
        self._entry = sysfs_entry

    def belongs_to(self, vendor_id, product_id):
        return self._hid_id() == (vendor_id, product_id)

    def is_raw_hid(self):
        return self._descriptor().startswith(RAW_HID_USAGE_PAGE)

    def device_path(self):
        return f"/dev/{self._entry.name}"

    def _hid_id(self):
        _bus, vendor, product = self._uevent()["HID_ID"].split(":")

        return int(vendor, 16), int(product, 16)

    def _uevent(self):
        lines = (self._entry / "device" / "uevent").read_text().splitlines()

        return dict(line.split("=", 1) for line in lines if "=" in line)

    def _descriptor(self):
        return (self._entry / "device" / "report_descriptor").read_bytes()
