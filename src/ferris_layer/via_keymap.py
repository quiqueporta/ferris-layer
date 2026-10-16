BYTES_PER_KEY = 2


class ViaKeymap:
    def __init__(self, backup, keys_per_layer):
        self._backup = backup
        self._keys_per_layer = keys_per_layer

    def layers(self):
        codes = self._keycodes(bytes.fromhex(self._backup["keymap"]))

        return [self._layer(number, codes) for number in range(self._backup["layers"])]

    def _keycodes(self, keymap):
        return [int.from_bytes(keymap[i:i + BYTES_PER_KEY], "big") for i in range(0, len(keymap), BYTES_PER_KEY)]

    def _layer(self, number, codes):
        return codes[number * self._keys_per_layer:(number + 1) * self._keys_per_layer]
