from ferris_layer.layer import Layer


class LayerNames:
    def __init__(self, names):
        self._names = names

    def layer(self, number):
        return Layer(number=number, name=self._names.get(number, f"Layer {number}"))
