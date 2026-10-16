from ferris_layer.via_backup import ViaBackup
from via_fakes import MATRIX_KEYS, REPORT_SIZE, FakeViaKeyboard


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
