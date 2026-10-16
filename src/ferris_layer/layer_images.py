from ferris_layer.keycode_labels import KeycodeLabels
from ferris_layer.layer_drawing import LayerDrawing
from ferris_layer.via_keymap import ViaKeymap
from ferris_layer.via_macros import ViaMacros


class LayerImages:
    def __init__(self, rows, cols, directory):
        self._rows = rows
        self._cols = cols
        self._directory = directory

    def write(self, backup):
        macros = ViaMacros(bytes.fromhex(backup["macros"])).labels()
        drawing = LayerDrawing(KeycodeLabels(macros), self._cols)
        keymap = ViaKeymap(backup, self._rows * self._cols)

        self._directory.mkdir(parents=True, exist_ok=True)
        for number, codes in enumerate(keymap.layers()):
            (self._directory / f"layer-{number}.svg").write_text(drawing.svg(codes))
