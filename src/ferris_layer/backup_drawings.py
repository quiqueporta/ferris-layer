from ferris_layer.keycode_labels import KeycodeLabels
from ferris_layer.layer_drawing import LayerDrawing
from ferris_layer.via_keymap import ViaKeymap
from ferris_layer.via_macros import ViaMacros


class BackupDrawings:
    def __init__(self, rows, cols):
        self._rows = rows
        self._cols = cols

    def svgs(self, backup):
        drawing = self._drawing_for(backup)

        return [drawing.svg(codes) for codes in ViaKeymap(backup, self._rows * self._cols).layers()]

    def svg(self, backup, number):
        return self.svgs(backup)[number]

    def _drawing_for(self, backup):
        macros = ViaMacros(bytes.fromhex(backup["macros"])).labels()

        return LayerDrawing(KeycodeLabels(macros), self._cols)
