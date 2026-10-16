LAYER_REPORT_PREFIX = b"LY"


class LayerReport:
    def __init__(self, raw):
        self._raw = raw

    def is_layer_change(self):
        return self._raw.startswith(LAYER_REPORT_PREFIX)

    def layer_number(self):
        return self._raw[len(LAYER_REPORT_PREFIX)]
