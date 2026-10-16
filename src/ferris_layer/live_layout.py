from ferris_layer.backup_drawings import BackupDrawings
from ferris_layer.ferris_sweep import MATRIX_COLS, MATRIX_ROWS
from ferris_layer.keyboard_keymap import KeyboardKeymap

BASE_LAYER = 0
UNREADABLE = "Cannot read the layout. Is the Ferris Sweep plugged in?"


class LiveLayout:
    def __init__(self, finder, open_keyboard, window, names):
        self._keymap = KeyboardKeymap(finder, open_keyboard, MATRIX_ROWS * MATRIX_COLS)
        self._drawings = BackupDrawings(MATRIX_ROWS, MATRIX_COLS)
        self._window = window
        self._layer = names.layer(BASE_LAYER)
        self._backup = None

    def show(self, layer):
        self._layer = layer

        if self._backup is not None:
            self._draw()

    def open(self):
        self._backup = self._keymap.read()

        if self._backup is None:
            self._window.show_message(UNREADABLE)
        else:
            self._draw()

    def close(self):
        self._backup = None

    def _draw(self):
        svg = self._drawings.svg(self._backup, self._layer.number)

        self._window.show(self._layer.description(), svg)
