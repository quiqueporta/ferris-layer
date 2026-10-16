#!/bin/sh
# Builds the Ferris Sweep firmware with the layer report, inside the official QMK Docker image.
# Usage: firmware/build.sh [keymap] [converter]    e.g. firmware/build.sh quique promicro_rp2040
set -eu

KEYMAP="${1:-quique}"
CONVERTER="${2:-promicro_rp2040}"
QMK_HOME="${QMK_HOME:-$HOME/qmk_firmware}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SOURCE="$HERE/keymaps/$KEYMAP"
TARGET="$QMK_HOME/keyboards/ferris/sweep/keymaps/$KEYMAP"

if [ ! -d "$SOURCE" ]; then
    echo "Keymap not found: $SOURCE" >&2
    exit 1
fi

if [ ! -d "$QMK_HOME/keyboards/ferris/sweep" ]; then
    echo "QMK not found at $QMK_HOME. Clone it first:" >&2
    echo "  git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/qmk/qmk_firmware.git $QMK_HOME" >&2
    exit 1
fi

rm -rf "$TARGET"
mkdir -p "$TARGET"
cp "$SOURCE"/keymap.c "$SOURCE"/rules.mk "$HERE"/layer_report/layer_report.c "$HERE"/layer_report/layer_report.h "$TARGET"/

docker run --rm \
    --user "$(id -u):$(id -g)" \
    -w /qmk_firmware \
    -v "$QMK_HOME":/qmk_firmware:z \
    -e SKIP_GIT=true \
    ghcr.io/qmk/qmk_cli \
    make "ferris/sweep:$KEYMAP" CONVERT_TO="$CONVERTER"

mkdir -p "$HERE/build"
rm -f "$HERE"/build/*.uf2
cp "$QMK_HOME"/ferris_sweep_"$KEYMAP"*.uf2 "$HERE/build/"
ls -l "$HERE/build"
