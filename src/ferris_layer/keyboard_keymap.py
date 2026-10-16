from ferris_layer.via_backup import ViaBackup


class KeyboardKeymap:
    def __init__(self, finder, open_keyboard, matrix_keys):
        self._finder = finder
        self._open_keyboard = open_keyboard
        self._backup = ViaBackup(matrix_keys)

    def read(self):
        path = self._finder.find()
        if path is None:
            return None

        try:
            return self._read_from(self._open_keyboard(path))
        except OSError:
            return None

    def _read_from(self, keyboard):
        try:
            return self._backup.save(keyboard)
        finally:
            keyboard.close()
