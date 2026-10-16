from ferris_layer.via_protocol import ViaProtocol


BYTES_PER_KEY = 2


class ViaBackup:
    def __init__(self, matrix_keys):
        self._matrix_keys = matrix_keys

    def save(self, keyboard):
        via = ViaProtocol(keyboard)
        layers = via.layer_count()
        keymap = via.read_keymap(layers * self._matrix_keys * BYTES_PER_KEY)
        macros = via.read_macros(via.macro_buffer_size())

        return {"layers": layers, "keymap": keymap.hex(), "macros": macros.hex()}

    def restore(self, keyboard, backup):
        via = ViaProtocol(keyboard)
        via.write_keymap(bytes.fromhex(backup["keymap"]))
        via.write_macros(bytes.fromhex(backup["macros"]))
