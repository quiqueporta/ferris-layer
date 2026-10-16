import os
import select

REPORT_SIZE = 32
TIMEOUT_SECONDS = 2


class HidrawDevice:
    def __init__(self, path):
        self._fd = os.open(path, os.O_RDWR)

    def write(self, data):
        os.write(self._fd, data)

    def read(self):
        ready, _, _ = select.select([self._fd], [], [], TIMEOUT_SECONDS)
        if not ready:
            raise TimeoutError("The keyboard does not answer over Raw HID")

        return os.read(self._fd, REPORT_SIZE)

    def close(self):
        os.close(self._fd)
