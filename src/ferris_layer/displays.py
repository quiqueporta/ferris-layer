class Displays:
    def __init__(self, *displays):
        self._displays = displays

    def show(self, layer):
        for display in self._displays:
            display.show(layer)
