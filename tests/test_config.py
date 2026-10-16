from ferris_layer.config import load_layer_names
from ferris_layer.layer import Layer


def test_reads_layer_names_from_the_config_file(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('[layers]\n0 = "Letters"\n2 = "Symbols"\n')

    names = load_layer_names(config)

    assert [names.layer(0), names.layer(2)] == [Layer(0, "Letters"), Layer(2, "Symbols")]


def test_uses_generic_names_without_a_config_file(tmp_path):
    names = load_layer_names(tmp_path / "missing.toml")

    assert names.layer(1) == Layer(1, "Layer 1")
