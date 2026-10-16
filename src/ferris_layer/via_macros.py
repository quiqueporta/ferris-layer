from ferris_layer.keycode_labels import BASIC_KEYS

MACRO_END = b"\x00"
ACTION_PREFIX = 0x01
ACTION_SIZE = 3
PRESSING_ACTIONS = (0x01, 0x02)


class ViaMacros:
    def __init__(self, buffer):
        self._buffer = buffer

    def labels(self):
        return [self._label(macro) for macro in self._buffer.split(MACRO_END)]

    def _label(self, macro):
        keys, text = [], ""
        position = 0
        while position < len(macro):
            if macro[position] == ACTION_PREFIX:
                keys += self._pressed_key(macro[position + 1:position + ACTION_SIZE])
                position += ACTION_SIZE
            else:
                text += chr(macro[position])
                position += 1

        return "+".join(keys) + text

    def _pressed_key(self, action):
        kind, code = action
        if kind not in PRESSING_ACTIONS:
            return []

        return [BASIC_KEYS[code]]
