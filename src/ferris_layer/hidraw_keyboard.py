import os

from ferris_layer.layer_report import LAYER_REPORT_PREFIX

REPORT_SIZE = 32
NO_REPORT_ID = b"\x00"


class HidrawKeyboard:
    def __init__(self, path):
        self._fd = os.open(path, os.O_RDWR)

    def request_current_layer(self):
        os.write(self._fd, NO_REPORT_ID + LAYER_REPORT_PREFIX.ljust(REPORT_SIZE, b"\x00"))

    def reports(self):
        while True:
            yield os.read(self._fd, REPORT_SIZE)

    def close(self):
        os.close(self._fd)
