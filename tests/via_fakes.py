REPORT_SIZE = 32
MATRIX_KEYS = 8 * 5


class FakeViaKeyboard:
    def __init__(self, layers, keymap, macros):
        self._layers = layers
        self.keymap = bytearray(keymap)
        self.macros = bytearray(macros)
        self._responses = []
        self.closed = False

    def write(self, data):
        report_id, command = data[0], data[1:]
        assert report_id == 0 and len(command) == REPORT_SIZE

        self._responses.append(self._answer(command).ljust(REPORT_SIZE, b"\x00"))

    def read(self):
        return self._responses.pop(0)

    def close(self):
        self.closed = True

    def _answer(self, command):
        command_id = command[0]
        offset = int.from_bytes(command[1:3], "big")
        size = command[3]

        if command_id == 0x11:
            return bytes([0x11, self._layers])
        if command_id == 0x0D:
            return bytes([0x0D]) + len(self.macros).to_bytes(2, "big")
        if command_id == 0x12:
            return bytes(command[:4]) + self.keymap[offset:offset + size]
        if command_id == 0x0E:
            return bytes(command[:4]) + self.macros[offset:offset + size]
        if command_id == 0x13:
            self.keymap[offset:offset + size] = command[4:4 + size]
            return bytes(command)
        if command_id == 0x0F:
            self.macros[offset:offset + size] = command[4:4 + size]
            return bytes(command)

        return bytes([0xFF])
