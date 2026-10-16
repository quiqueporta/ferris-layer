import tomllib
from pathlib import Path

from ferris_layer.layer_names import LayerNames


def load_layer_names(path):
    path = Path(path)
    if not path.exists():
        return LayerNames({})

    layers = tomllib.loads(path.read_text())["layers"]

    return LayerNames({int(number): name for number, name in layers.items()})
