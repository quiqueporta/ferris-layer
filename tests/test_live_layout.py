import xml.etree.ElementTree as ElementTree

from ferris_layer.layer import Layer
from ferris_layer.layer_names import LayerNames
from ferris_layer.live_layout import LiveLayout
from via_fakes import MATRIX_KEYS, FakeViaKeyboard


SVG = "{http://www.w3.org/2000/svg}"
Q = 0x14
ONE = 0x1E


class FinderStub:
    def __init__(self, path):
        self._path = path

    def find(self):
        return self._path


class WindowSpy:
    def __init__(self):
        self.shown = []
        self.messages = []

    def show_message(self, text):
        self.messages.append(text)

    def show(self, title, svg):
        labels = [text.text for text in ElementTree.fromstring(svg).iter(f"{SVG}text")]
        self.shown.append((title, labels))


def keymap_with(*layers):
    codes = []
    for keys in layers:
        layer = [0x0000] * MATRIX_KEYS
        for (row, col), code in keys.items():
            layer[row * 5 + col] = code
        codes += layer

    return b"".join(code.to_bytes(2, "big") for code in codes)


def live_layout(keyboard, window, path="/dev/hidraw2"):
    return LiveLayout(
        finder=FinderStub(path),
        open_keyboard=lambda _path: keyboard,
        window=window,
        names=LayerNames({0: "Letters"}),
    )


def test_opening_shows_the_active_layer_as_the_keyboard_has_it():
    keyboard = FakeViaKeyboard(layers=2, keymap=keymap_with({(0, 0): Q}, {(0, 0): ONE}), macros=b"")
    window = WindowSpy()
    live = live_layout(keyboard, window)

    live.show(Layer(1, "Numbers"))
    live.open()

    assert window.shown == [("Layer 1 · Numbers", ["1"])]


def test_follows_layer_changes_while_open():
    keyboard = FakeViaKeyboard(layers=2, keymap=keymap_with({(0, 0): Q}, {(0, 0): ONE}), macros=b"")
    window = WindowSpy()
    live = live_layout(keyboard, window)

    live.show(Layer(1, "Numbers"))
    live.open()
    live.show(Layer(0, "Letters"))

    assert window.shown[-1] == ("Layer 0 · Letters", ["Q"])


def test_does_not_draw_while_closed():
    keyboard = FakeViaKeyboard(layers=2, keymap=keymap_with({(0, 0): Q}, {(0, 0): ONE}), macros=b"")
    window = WindowSpy()
    live = live_layout(keyboard, window)

    live.show(Layer(1, "Numbers"))
    live.open()
    live.close()
    live.show(Layer(0, "Letters"))

    assert len(window.shown) == 1


def test_reopening_shows_the_changes_made_in_via_meanwhile():
    keyboard = FakeViaKeyboard(layers=1, keymap=keymap_with({(0, 0): Q}), macros=b"")
    window = WindowSpy()
    live = live_layout(keyboard, window)

    live.show(Layer(0, "Letters"))
    live.open()
    live.close()
    keyboard.keymap[0:2] = ONE.to_bytes(2, "big")
    live.open()

    assert window.shown[-1] == ("Layer 0 · Letters", ["1"])


class SilentKeyboard:
    def write(self, data):
        pass

    def read(self):
        raise TimeoutError("The keyboard does not answer over Raw HID")

    def close(self):
        pass


def test_says_so_when_the_keyboard_is_not_connected():
    window = WindowSpy()
    live = live_layout(keyboard=None, window=window, path=None)

    live.show(Layer(0, "Letters"))
    live.open()

    assert (window.shown, window.messages) == ([], ["Cannot read the layout. Is the Ferris Sweep plugged in?"])


def test_says_so_when_the_keyboard_does_not_answer():
    window = WindowSpy()
    live = live_layout(SilentKeyboard(), window)

    live.show(Layer(0, "Letters"))
    live.open()

    assert (window.shown, window.messages) == ([], ["Cannot read the layout. Is the Ferris Sweep plugged in?"])


def test_releases_the_keyboard_after_reading_it():
    keyboard = FakeViaKeyboard(layers=1, keymap=keymap_with({(0, 0): Q}), macros=b"")
    live = live_layout(keyboard, WindowSpy())

    live.show(Layer(0, "Letters"))
    live.open()

    assert keyboard.closed


def test_shows_the_base_layer_until_the_keyboard_announces_one():
    keyboard = FakeViaKeyboard(layers=2, keymap=keymap_with({(0, 0): Q}, {(0, 0): ONE}), macros=b"")
    window = WindowSpy()

    live_layout(keyboard, window).open()

    assert window.shown == [("Layer 0 · Letters", ["Q"])]
