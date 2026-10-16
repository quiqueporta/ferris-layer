from ferris_layer.displays import Displays
from ferris_layer.layer import Layer


class DisplaySpy:
    def __init__(self):
        self.shown = []

    def show(self, layer):
        self.shown.append(layer)


def test_shows_the_layer_on_every_display():
    tray, window = DisplaySpy(), DisplaySpy()

    Displays(tray, window).show(Layer(2, "Numbers"))

    assert (tray.shown, window.shown) == ([Layer(2, "Numbers")], [Layer(2, "Numbers")])
