import pytest

from ferris_layer.keycode_labels import KeycodeLabels, KeyLabel


@pytest.mark.parametrize(
    ("code", "label"),
    [
        (0x04, "A"),
        (0x1E, "1"),
        (0x27, "0"),
        (0x28, "Enter"),
        (0x29, "Esc"),
        (0x2A, "Bksp"),
        (0x2B, "Tab"),
        (0x2C, "Space"),
        (0x2D, "-"),
        (0x36, ","),
        (0x38, "/"),
        (0x39, "Caps"),
        (0x3A, "F1"),
        (0x45, "F12"),
        (0x4C, "Del"),
        (0x4F, "→"),
        (0x52, "↑"),
        (0x53, "NumLk"),
        (0x55, "×"),
        (0x62, "0"),
        (0x67, "="),
        (0x6F, "F20"),
        (0xA8, "Mute"),
        (0xAA, "Vol-"),
        (0xB2, "Calc"),
        (0xE0, "Ctrl"),
        (0xE3, "Win"),
        (0xE5, "RShift"),
    ],
)
def test_names_basic_keys_as_printed_on_the_keycap(code, label):
    assert KeycodeLabels().label(code) == KeyLabel(label)


@pytest.mark.parametrize(
    ("code", "label"),
    [(0x021E, "!"), (0x021F, "@"), (0x022D, "_"), (0x0231, "|"), (0x0233, ":"), (0x0234, '"'), (0x0235, "~")],
)
def test_shows_the_symbol_typed_with_shift(code, label):
    assert KeycodeLabels().label(code) == KeyLabel(label)


def test_marks_transparent_keys_with_a_triangle():
    assert KeycodeLabels().label(0x0001) == KeyLabel("▽")


def test_names_the_layer_a_to_key_switches_to():
    assert KeycodeLabels().label(0x5203) == KeyLabel("TO(3)")


def test_shows_unknown_keycodes_in_hexadecimal():
    assert KeycodeLabels().label(0x7C16) == KeyLabel("0x7C16")
