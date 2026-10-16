import re
from pathlib import Path

from ferris_layer.layer import Layer
from ferris_layer.layer_icons import LayerIcons


def fill_of(svg):
    return re.search(r'<rect[^>]*fill="([^"]+)"', svg).group(1)


def test_the_icon_shows_the_layer_number(tmp_path):
    icons = LayerIcons(directory=tmp_path)

    svg = Path(icons.icon_for(Layer(2, "Numbers"))).read_text()

    assert re.search(r"<text[^>]*>2</text>", svg)


def test_each_layer_has_its_own_color(tmp_path):
    icons = LayerIcons(directory=tmp_path)

    fills = {fill_of(Path(icons.icon_for(Layer(n, f"Layer {n}"))).read_text()) for n in range(4)}

    assert len(fills) == 4
