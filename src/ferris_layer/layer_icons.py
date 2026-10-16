from pathlib import Path

PALETTE = ("#6b7280", "#2563eb", "#16a34a", "#ea580c")

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <rect x="2" y="2" width="60" height="60" rx="14" fill="{color}"/>
  <text x="32" y="47" text-anchor="middle" font-family="Ubuntu, sans-serif" font-size="44" font-weight="bold" fill="#ffffff">{number}</text>
</svg>
"""


class LayerIcons:
    def __init__(self, directory):
        self._directory = Path(directory)

    def icon_for(self, layer):
        path = self._directory / f"layer-{layer.number}.svg"
        path.write_text(SVG_TEMPLATE.format(color=self._color_of(layer), number=layer.number))

        return str(path)

    def _color_of(self, layer):
        return PALETTE[layer.number % len(PALETTE)]
