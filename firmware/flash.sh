#!/bin/sh
# Copies the built firmware to one keyboard half in bootloader mode, waiting for its RPI-RP2 drive to appear.
# Usage: firmware/flash.sh
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
WAIT_SECONDS=120

FIRMWARE="$(ls "$HERE"/build/*.uf2 2>/dev/null | head -n 1)"
if [ -z "$FIRMWARE" ]; then
    echo "No firmware in $HERE/build. Build it first with: make firmware" >&2
    exit 1
fi

drive() {
    findmnt -rno TARGET -S LABEL=RPI-RP2 || true
}

cat <<'EOF'
Put ONE half into bootloader mode:

  1. Unplug the USB cable from the keyboard.
  2. Only then unplug the TRRS cable between the halves.
     Never plug or unplug the TRRS cable while USB is connected: it can short and damage the controller.
  3. Hold the outer top key of the half you are flashing (Q on the left, P on the right)
     and, while holding it, plug the USB cable into THAT half.

Waiting for the RPI-RP2 drive...
EOF

DRIVE=""
for _ in $(seq "$WAIT_SECONDS"); do
    DRIVE="$(drive)"
    [ -n "$DRIVE" ] && break
    sleep 1
done

if [ -z "$DRIVE" ]; then
    echo "The RPI-RP2 drive did not appear in $WAIT_SECONDS seconds." >&2
    exit 1
fi

echo "Copying $(basename "$FIRMWARE") to $DRIVE. Do not unplug anything yet..."
cp "$FIRMWARE" "$DRIVE/"
sync

for _ in $(seq "$WAIT_SECONDS"); do
    [ -z "$(drive)" ] && break
    sleep 1
done

cat <<'EOF'
Done: the half has rebooted with the new firmware. You can unplug its USB cable now.

  - If this was the first half, run `make flash` again for the other one.
  - When both halves are flashed: with USB unplugged, connect the TRRS cable,
    then plug USB into the left half as usual.
EOF
