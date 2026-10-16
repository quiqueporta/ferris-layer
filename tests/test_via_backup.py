from ferris_layer.via_backup import ViaBackup


REPORT_SIZE = 32
MATRIX_KEYS = 8 * 5


class FakeViaKeyboard:
    def __init__(self, layers, keymap, macros):
        self._layers = layers
        self.keymap = bytearray(keymap)
        self.macros = bytearray(macros)
        self._responses = []

    def write(self, data):
        report_id, command = data[0], data[1:]
        assert report_id == 0 and len(command) == REPORT_SIZE

        self._responses.append(self._answer(command).ljust(REPORT_SIZE, b"\x00"))

    def read(self):
        return self._responses.pop(0)

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


def keymap_of(layers):
    return bytes(i % 256 for i in range(layers * MATRIX_KEYS * 2))


def test_saves_and_restores_the_keymap_and_macros():
    original = FakeViaKeyboard(layers=4, keymap=keymap_of(4), macros=b"\x01hello\x00" * 30)
    backup = ViaBackup(matrix_keys=MATRIX_KEYS).save(original)

    flashed = FakeViaKeyboard(layers=4, keymap=bytes(len(keymap_of(4))), macros=bytes(180))
    ViaBackup(matrix_keys=MATRIX_KEYS).restore(flashed, backup)

    assert (flashed.keymap, flashed.macros) == (original.keymap, original.macros)


def test_ignores_layer_reports_arriving_between_responses():
    keyboard = FakeViaKeyboard(layers=1, keymap=keymap_of(1), macros=b"")
    keyboard.read = _with_layer_report_first(keyboard.read)

    backup = ViaBackup(matrix_keys=MATRIX_KEYS).save(keyboard)

    assert backup["layers"] == 1


def _with_layer_report_first(read):
    pending = [b"LY\x02".ljust(REPORT_SIZE, b"\x00")]

    def read_with_noise():
        return pending.pop() if pending else read()

    return read_with_noise
