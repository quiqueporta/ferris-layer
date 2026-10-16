from ferris_layer.hidraw_finder import HidrawFinder


KEYBOARD_DESCRIPTOR = bytes([0x05, 0x01, 0x09, 0x06, 0xA1, 0x01])
RAW_HID_DESCRIPTOR = bytes([0x06, 0x60, 0xFF, 0x09, 0x61, 0xA1, 0x01])
FERRIS_ID = "HID_ID=0003:0000C2AB:00003939"


def add_hidraw(sysfs, name, hid_id, descriptor):
    device = sysfs / name / "device"
    device.mkdir(parents=True)
    (device / "uevent").write_text(f"DRIVER=hid-generic\n{hid_id}\nHID_NAME=Something\n")
    (device / "report_descriptor").write_bytes(descriptor)


def test_finds_the_keyboard_raw_hid_interface(tmp_path):
    add_hidraw(tmp_path, "hidraw0", "HID_ID=0018:000004F3:0000316F", RAW_HID_DESCRIPTOR)
    add_hidraw(tmp_path, "hidraw1", FERRIS_ID, KEYBOARD_DESCRIPTOR)
    add_hidraw(tmp_path, "hidraw2", FERRIS_ID, RAW_HID_DESCRIPTOR)
    finder = HidrawFinder(sysfs=tmp_path, vendor_id=0xC2AB, product_id=0x3939)

    assert finder.find() == "/dev/hidraw2"


def test_finds_nothing_when_the_keyboard_is_unplugged(tmp_path):
    add_hidraw(tmp_path, "hidraw1", FERRIS_ID, KEYBOARD_DESCRIPTOR)
    finder = HidrawFinder(sysfs=tmp_path, vendor_id=0xC2AB, product_id=0x3939)

    assert finder.find() is None
