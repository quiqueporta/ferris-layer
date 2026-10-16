import math
from xml.sax.saxutils import escape

from ferris_layer.sweep_layout import SWEEP_KEYS

UNIT = 64
KEY_SIZE = 58
MARGIN = 8

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
{keys}</svg>
"""

KEY_TEMPLATE = """  <g{transform}>
    <rect x="{x}" y="{y}" width="{size}" height="{size}" rx="8" fill="#f4f4f5" stroke="#a1a1aa"/>
{label}  </g>
"""

TEXT_TEMPLATE = """    <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="central" font-family="Ubuntu, sans-serif" font-size="{font_size}" fill="{color}">{label}</text>
"""

TAP_FONT_SIZE = 16
TAP_COLOR = "#18181b"
HOLD_FONT_SIZE = 11
HOLD_COLOR = "#71717a"
HOLD_OFFSET = 18
LABEL_WIDTH = 52
CHARACTER_WIDTH = 0.6


class LayerDrawing:
    def __init__(self, labels, cols):
        self._labels = labels
        self._cols = cols

    def svg(self, codes):
        keys = "".join(self._key(codes[self._index_of(key.position)], key) for key in SWEEP_KEYS)
        width, height = self._canvas_size()

        return SVG_TEMPLATE.format(width=width, height=height, keys=keys)

    def _index_of(self, position):
        row, col = position

        return row * self._cols + col

    def _key(self, code, key):
        centre_x, centre_y = self._centre(key.x), self._centre(key.y)

        return KEY_TEMPLATE.format(
            transform=self._rotation(key.rotation, centre_x, centre_y),
            x=self._pixels(key.x),
            y=self._pixels(key.y),
            size=KEY_SIZE,
            label=self._label(code, centre_x, centre_y),
        )

    def _canvas_size(self):
        right = max(self._centre(key.x) + self._half_extent(key.rotation) for key in SWEEP_KEYS)
        bottom = max(self._centre(key.y) + self._half_extent(key.rotation) for key in SWEEP_KEYS)

        return math.ceil(right + MARGIN), math.ceil(bottom + MARGIN)

    def _centre(self, units):
        return self._pixels(units) + KEY_SIZE / 2

    def _half_extent(self, angle):
        radians = math.radians(angle)

        return KEY_SIZE / 2 * (abs(math.cos(radians)) + abs(math.sin(radians)))

    def _rotation(self, angle, centre_x, centre_y):
        if not angle:
            return ""

        return f' transform="rotate({angle} {centre_x} {centre_y})"'

    def _label(self, code, centre_x, centre_y):
        label = self._labels.label(code)

        tap = self._text(label.tap, centre_x, centre_y, self._fitting_font_size(label.tap), TAP_COLOR)
        hold = self._text(label.hold, centre_x, centre_y + HOLD_OFFSET, HOLD_FONT_SIZE, HOLD_COLOR)

        return tap + hold

    def _fitting_font_size(self, text):
        fitting = LABEL_WIDTH / (max(len(text), 1) * CHARACTER_WIDTH)

        return min(TAP_FONT_SIZE, math.floor(fitting * 10) / 10)

    def _text(self, text, x, y, font_size, color):
        if not text:
            return ""

        return TEXT_TEMPLATE.format(x=x, y=y, font_size=font_size, color=color, label=escape(text))

    def _pixels(self, units):
        return MARGIN + round(units * UNIT, 1)
