import string
from typing import NamedTuple

LETTERS = {0x04 + index: letter for index, letter in enumerate(string.ascii_uppercase)}
DIGITS = {0x1E + index: digit for index, digit in enumerate("1234567890")}
FUNCTION_KEYS = {0x3A + index: f"F{index + 1}" for index in range(12)} | {
    0x68 + index: f"F{index + 13}" for index in range(12)
}

BASIC_KEYS = LETTERS | DIGITS | FUNCTION_KEYS | {
    0x00: "", 0x01: "▽",
    0x28: "Enter", 0x29: "Esc", 0x2A: "Bksp", 0x2B: "Tab", 0x2C: "Space",
    0x2D: "-", 0x2E: "=", 0x2F: "[", 0x30: "]", 0x31: "\\", 0x32: "#", 0x33: ";", 0x34: "'", 0x35: "`",
    0x36: ",", 0x37: ".", 0x38: "/", 0x39: "Caps",
    0x46: "PrtSc", 0x47: "ScrLk", 0x48: "Pause", 0x49: "Ins", 0x4A: "Home", 0x4B: "PgUp",
    0x4C: "Del", 0x4D: "End", 0x4E: "PgDn", 0x4F: "→", 0x50: "←", 0x51: "↓", 0x52: "↑",
    0x53: "NumLk", 0x54: "÷", 0x55: "×", 0x56: "−", 0x57: "+", 0x58: "Enter",
    0x59: "1", 0x5A: "2", 0x5B: "3", 0x5C: "4", 0x5D: "5", 0x5E: "6", 0x5F: "7", 0x60: "8", 0x61: "9",
    0x62: "0", 0x63: ".", 0x64: "\\", 0x65: "Menu", 0x67: "=",
    0xA5: "Power", 0xA6: "Sleep", 0xA7: "Wake", 0xA8: "Mute", 0xA9: "Vol+", 0xAA: "Vol-",
    0xAB: "Next", 0xAC: "Prev", 0xAD: "Stop", 0xAE: "Play", 0xAF: "Select", 0xB0: "Eject",
    0xB1: "Mail", 0xB2: "Calc", 0xB3: "My PC",
    0xE0: "Ctrl", 0xE1: "Shift", 0xE2: "Alt", 0xE3: "Win",
    0xE4: "RCtrl", 0xE5: "RShift", 0xE6: "AltGr", 0xE7: "RWin",
}


SHIFTED_SYMBOLS = {
    0x1E: "!", 0x1F: "@", 0x20: "#", 0x21: "$", 0x22: "%", 0x23: "^", 0x24: "&", 0x25: "*", 0x26: "(", 0x27: ")",
    0x2D: "_", 0x2E: "+", 0x2F: "{", 0x30: "}", 0x31: "|", 0x33: ":", 0x34: '"', 0x35: "~",
    0x36: "<", 0x37: ">", 0x38: "?",
}

BASIC_KEY_MASK = 0x00FF
MODIFIERS_MASK = 0xFF00
LEFT_SHIFT = 0x0200
LAYER_SWITCH = 0x5200
LAYER_MASK = 0x1F
MOD_TAP = 0x2000
LAYER_TAP = 0x4000
MOD_TAP_KIND_MASK = 0xE000
LAYER_TAP_KIND_MASK = 0xF000
HOLD_SHIFT = 8
TAP_LAYER_MASK = 0x0F
MOD_BITS_MASK = 0x1F
RIGHT_HAND_MODS = 0x10
MACRO = 0x7700
MACRO_MASK = 0x7F
MOD_NAMES = ((0x01, "Ctrl"), (0x02, "Shift"), (0x04, "Alt"), (0x08, "Win"))


class KeyLabel(NamedTuple):
    tap: str
    hold: str = ""


class BasicKeys:
    def knows(self, code):
        return code in BASIC_KEYS

    def label(self, code):
        return KeyLabel(BASIC_KEYS[code])


class ShiftedSymbols:
    def knows(self, code):
        return code & MODIFIERS_MASK == LEFT_SHIFT and code & BASIC_KEY_MASK in SHIFTED_SYMBOLS

    def label(self, code):
        return KeyLabel(SHIFTED_SYMBOLS[code & BASIC_KEY_MASK])


class LayerSwitches:
    def knows(self, code):
        return code & ~LAYER_MASK == LAYER_SWITCH

    def label(self, code):
        return KeyLabel(f"TO({code & LAYER_MASK})")


class ModTaps:
    def knows(self, code):
        return code & MOD_TAP_KIND_MASK == MOD_TAP and code & BASIC_KEY_MASK in BASIC_KEYS

    def label(self, code):
        mods = code >> HOLD_SHIFT & MOD_BITS_MASK
        side = "R" if mods & RIGHT_HAND_MODS else ""
        names = "+".join(side + name for bit, name in MOD_NAMES if mods & bit)

        return KeyLabel(BASIC_KEYS[code & BASIC_KEY_MASK], names)


class LayerTaps:
    def knows(self, code):
        return code & LAYER_TAP_KIND_MASK == LAYER_TAP and code & BASIC_KEY_MASK in BASIC_KEYS

    def label(self, code):
        return KeyLabel(BASIC_KEYS[code & BASIC_KEY_MASK], f"L{code >> HOLD_SHIFT & TAP_LAYER_MASK}")


class Macros:
    def __init__(self, labels):
        self._labels = labels

    def knows(self, code):
        return code & ~MACRO_MASK == MACRO and code & MACRO_MASK < len(self._labels)

    def label(self, code):
        return KeyLabel(self._labels[code & MACRO_MASK])


class KeycodeLabels:
    def __init__(self, macros=()):
        self._families = (BasicKeys(), ShiftedSymbols(), LayerSwitches(), ModTaps(), LayerTaps(), Macros(macros))

    def label(self, code):
        for family in self._families:
            if family.knows(code):
                return family.label(code)

        return KeyLabel(f"0x{code:04X}")
