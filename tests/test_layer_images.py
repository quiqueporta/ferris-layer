import json
import math
import xml.etree.ElementTree as ElementTree

from ferris_layer.via_backup_cli import main


MATRIX_KEYS = 8 * 5


def write_backup(path, layers, macros=b""):
    keymap = b"".join(code.to_bytes(2, "big") for layer in layers for code in layer)
    path.write_text(json.dumps({"layers": len(layers), "keymap": keymap.hex(), "macros": macros.hex()}))

    return path


SVG = "{http://www.w3.org/2000/svg}"


def blank_layer():
    return [0x0000] * MATRIX_KEYS


def layer_with(keys):
    layer = blank_layer()
    for (row, col), code in keys.items():
        layer[row * 5 + col] = code

    return layer


def image(tmp_path, layers, number=0, macros=b""):
    backup = write_backup(tmp_path / "backup.json", layers, macros)
    main(["images", str(backup), str(tmp_path / "layers")])

    return ElementTree.parse(tmp_path / "layers" / f"layer-{number}.svg").getroot()


def labels_of(svg):
    return [text.text for text in svg.iter(f"{SVG}text")]


def test_writes_one_svg_image_per_layer(tmp_path):
    backup = write_backup(tmp_path / "backup.json", [blank_layer(), blank_layer()])

    main(["images", str(backup), str(tmp_path / "layers")])

    assert sorted(path.name for path in (tmp_path / "layers").iterdir()) == ["layer-0.svg", "layer-1.svg"]


def test_draws_the_34_keys_of_the_sweep(tmp_path):
    svg = image(tmp_path, [blank_layer()])

    assert len(list(svg.iter(f"{SVG}rect"))) == 34


def test_labels_each_key_with_what_it_types(tmp_path):
    svg = image(tmp_path, [layer_with({(0, 0): 0x14, (4, 4): 0x13})])

    assert labels_of(svg) == ["Q", "P"]


def test_tilts_the_thumb_keys_towards_the_centre(tmp_path):
    svg = image(tmp_path, [blank_layer()])

    rotations = [key.get("transform").split("(")[1].split()[0] for key in svg.iter(f"{SVG}g") if key.get("transform")]

    assert rotations == ["15", "30", "-30", "-15"]


def test_keys_that_do_something_else_when_held_show_both_actions(tmp_path):
    svg = image(tmp_path, [layer_with({(2, 0): 0x241D, (6, 4): 0x3428, (7, 0): 0x412C})])

    assert labels_of(svg) == ["Z", "Alt", "Enter", "RAlt", "Space", "L1"]


def test_labels_macros_with_what_they_do(tmp_path):
    win_l = bytes.fromhex("0102e3 01020f 01030f 0103e3")
    esc = bytes.fromhex("010129")
    macros = win_l + b"\x00" + esc + b"\x00" + b"hi" + b"\x00"

    svg = image(tmp_path, [layer_with({(0, 0): 0x7700, (0, 1): 0x7701, (0, 2): 0x7702})], macros=macros)

    assert labels_of(svg) == ["Win+L", "Esc", "hi"]


def test_shrinks_long_labels_to_fit_the_key(tmp_path):
    ctrl_alt_left = bytes.fromhex("0102e0 0102e2 010250 010350 0103e2 0103e0")

    svg = image(tmp_path, [layer_with({(0, 0): 0x14, (0, 1): 0x7700})], macros=ctrl_alt_left + b"\x00")

    short, long = (float(text.get("font-size")) for text in svg.iter(f"{SVG}text"))
    assert long * len("Ctrl+Alt+←") * 0.6 <= 52 < short * len("Ctrl+Alt+←") * 0.6


def test_the_whole_keyboard_fits_in_the_image(tmp_path):
    svg = image(tmp_path, [blank_layer()])

    width, height = float(svg.get("width")), float(svg.get("height"))
    corners = [corner for key in svg.iter(f"{SVG}g") for corner in corners_of(key)]

    assert all(0 <= x <= width and 0 <= y <= height for x, y in corners)


def corners_of(key):
    rect = key.find(f"{SVG}rect")
    left, top, size = (float(rect.get(name)) for name in ("x", "y", "width"))
    angle, centre_x, centre_y = rotation_of(key)

    return [
        rotated(x, y, angle, centre_x, centre_y)
        for x in (left, left + size)
        for y in (top, top + size)
    ]


def rotation_of(key):
    transform = key.get("transform")
    if not transform:
        return 0.0, 0.0, 0.0

    return tuple(float(number) for number in transform[len("rotate("):-1].split())


def rotated(x, y, angle, centre_x, centre_y):
    radians = math.radians(angle)
    dx, dy = x - centre_x, y - centre_y

    return (
        centre_x + dx * math.cos(radians) - dy * math.sin(radians),
        centre_y + dx * math.sin(radians) + dy * math.cos(radians),
    )
