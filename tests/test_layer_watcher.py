from ferris_layer.layer_watcher import LayerWatcher
from ferris_layer.layer import Layer
from ferris_layer.layer_names import LayerNames


REPORT_SIZE = 32


def layer_report(number):
    report = bytes([0x4C, 0x59, number])

    return report.ljust(REPORT_SIZE, b"\x00")


class DisplaySpy:
    def __init__(self):
        self.shown = []

    def show(self, layer):
        self.shown.append(layer)


def test_shows_the_layer_announced_by_the_keyboard():
    display = DisplaySpy()
    watcher = LayerWatcher(display=display, names=LayerNames({2: "Symbols"}))

    watcher.watch([layer_report(2)])

    assert display.shown == [Layer(number=2, name="Symbols")]


def test_ignores_reports_that_are_not_layer_changes():
    display = DisplaySpy()
    watcher = LayerWatcher(display=display, names=LayerNames({1: "Navigation"}))
    via_response = bytes([0x02, 0x00, 0x01]).ljust(REPORT_SIZE, b"\x00")

    watcher.watch([via_response, layer_report(1)])

    assert display.shown == [Layer(number=1, name="Navigation")]


def test_shows_a_generic_name_when_the_layer_has_none():
    display = DisplaySpy()
    watcher = LayerWatcher(display=display, names=LayerNames({}))

    watcher.watch([layer_report(3)])

    assert display.shown == [Layer(number=3, name="Layer 3")]
