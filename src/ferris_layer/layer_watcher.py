from ferris_layer.layer_report import LayerReport


class LayerWatcher:
    def __init__(self, display, names):
        self._display = display
        self._names = names

    def watch(self, reports):
        for raw in reports:
            self._show_if_layer_change(LayerReport(raw))

    def _show_if_layer_change(self, report):
        if not report.is_layer_change():
            return

        self._display.show(self._names.layer(report.layer_number()))
