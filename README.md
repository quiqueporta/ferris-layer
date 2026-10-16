# ferris-layer

Shows the active layer of a [Ferris Sweep](https://github.com/davidphilipbarr/Sweep) running QMK as a coloured icon in the GNOME top bar.

![Layer icons](docs/tray-icons.png)

Keyboard layers only exist inside the firmware: the computer just receives the final keys. This project adds a tiny piece of firmware that tells the computer which layer is active, and a small desktop app that turns that into a tray icon.

## How it works

```
 Ferris Sweep (QMK + VIA)                         Ubuntu / GNOME
┌─────────────────────────┐    Raw HID     ┌──────────────────────────────┐
│ layer_state_set_user()  │ ── "LY" + n ─▶ │ ferris-layer (systemd --user)│
│ via_command_kb()        │ ◀─ "LY" ────── │  reads /dev/hidrawN          │
└─────────────────────────┘                │  updates the top bar icon    │
                                           └──────────────────────────────┘
```

- On every layer change the firmware sends a 32-byte Raw HID report: `'L' 'Y' <layer>`.
- When the app connects it sends `'L' 'Y'` and the firmware answers with the current layer, so the icon is right from the start.
- VIA keeps working: the reports share the VIA Raw HID channel and use a prefix that no VIA command uses.
- If the keyboard is unplugged the app waits and reconnects on its own.

## Requirements

- Ubuntu (or another Debian-based distro) with GNOME. Tested on Ubuntu 24.04 on X11.
- A Ferris Sweep with QMK. The build script defaults to a Pro Micro RP2040 and supports any QMK converter (`elite_pi`, `kb2040`, `sparkfun_pm2040`…).
- [uv](https://docs.astral.sh/uv/getting-started/installation/) and Docker (to build the firmware).

## Commands

Everything goes through `make`. Run `make` alone to list the commands:

| Command | What it does |
| --- | --- |
| `make install` | Install the top bar app (asks for sudo). |
| `make backup` | Save the keyboard's VIA keymap and macros. |
| `make restore` | Write the backup back to the keyboard. |
| `make keymap` | Generate the QMK `keymap.c` from the backup. |
| `make images` | Draw every layer of the backup as SVG images. |
| `make firmware` | Build the firmware with Docker. |
| `make flash` | Wait for a half in bootloader mode and copy the firmware to it. |
| `make test` | Run the tests. |
| `make run` | Run the top bar app from the source tree. |

They work on the author's keymap by default. Pass `KEYMAP=myname` to use `firmware/keymaps/myname/` and its `via-backup.json`, `CONVERTER=elite_pi` for another controller, `BACKUP=path.json` for a backup somewhere else and `IMAGES=folder` to draw the images somewhere else.

## Install the desktop app

```sh
git clone https://github.com/quiqueporta/ferris-layer.git
cd ferris-layer
make install
```

`make install` runs `install.sh`, which:

1. Installs the system packages it needs: `python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-ayatanaappindicator3-0.1` and `gnome-shell-extension-appindicator`.
2. Creates a virtualenv with uv on the system Python with `--system-site-packages`. GTK bindings are much easier to get from apt than to build from PyPI.
3. Installs a udev rule so your user can read the keyboard's `/dev/hidraw` device without root.
4. Copies `config.example.toml` to `~/.config/ferris-layer/config.toml`.
5. Installs and starts the `ferris-layer` systemd user service.

On Ubuntu the AppIndicator extension is enabled by default. On other GNOME distros enable it with `gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com`.

### Layer names

The icon menu shows the layer name. Edit `~/.config/ferris-layer/config.toml`:

```toml
[layers]
0 = "Letters"
1 = "Symbols"
2 = "Numbers"
3 = "Functions"
```

Layers without a name are shown as `Layer N`. Restart the service after editing: `systemctl --user restart ferris-layer`.

## Firmware

Every command takes `KEYMAP=myname` to work on your own keymap folder, `firmware/keymaps/myname/`. The backup lives in that folder as `via-backup.json`.

> [!WARNING]
> **Never plug or unplug the TRRS cable between the halves while the USB cable is connected.** It can short and damage the controller. Always unplug USB first, and plug it back last.

### 1. Back up your VIA configuration

Flashing a new VIA firmware usually wipes the keymap and macros stored in the keyboard's EEPROM. With the keyboard plugged in as usual, save them first:

```sh
mkdir -p firmware/keymaps/myname
make backup KEYMAP=myname
```

### 2. Create your keymap

Generate a QMK keymap from the backup. It boots with exactly your current layout, and the layer report is already wired in:

```sh
cp firmware/keymaps/quique/rules.mk firmware/keymaps/myname/
make keymap KEYMAP=myname
```

If you already have your own QMK keymap, add the files from `firmware/layer_report/` to it and add these lines:

```c
#include "layer_report.h"

layer_state_t layer_state_set_user(layer_state_t state) {
    layer_report_announce(state);

    return state;
}

bool via_command_kb(uint8_t *data, uint8_t length) {
    return layer_report_answer(data);
}
```

```make
# rules.mk
VIA_ENABLE = yes
SRC += layer_report.c
```

### 3. Build

Clone QMK once, then build inside the official QMK Docker image:

```sh
git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/qmk/qmk_firmware.git ~/qmk_firmware
make firmware KEYMAP=myname
```

The firmware ends up in `firmware/build/`. Add `CONVERTER=elite_pi` (or your controller) if it is not a Pro Micro RP2040, and set `QMK_HOME` if QMK lives somewhere else.

### 4. Flash both halves

Both halves need the same firmware, so they keep understanding each other over the TRRS cable. Flash them one at a time, each with its own USB connection.

**Left half**

1. Run `make flash`. It waits up to two minutes for the half to show up.
2. Unplug the USB cable from the keyboard.
3. Only then, unplug the TRRS cable between the halves.
4. Hold `Q` (the outer top key of the left half) and, while holding it, plug the USB cable into the left half. This is QMK bootmagic: instead of starting as a keyboard, the half shows up as a drive called `RPI-RP2`.
5. `make flash` copies the firmware to it. The half reboots by itself and the drive disappears. Do not unplug anything until `make flash` says it is done.
6. Unplug the USB cable.

**Right half**

7. Run `make flash` again.
8. Hold `P` (the outer top key of the right half) and, while holding it, plug the USB cable **directly into the right half**.
9. Wait until `make flash` says it is done, then unplug the USB cable.

**Put it back together**

10. With USB still unplugged, connect the TRRS cable between the halves.
11. Plug the USB cable into the left half, without holding any key.
12. Type on both halves to check that they work.

If the `RPI-RP2` drive does not appear, the firmware you have now may not have bootmagic. Use a `QK_BOOT` key instead: assign it in VIA to a key on some layer, plug in the half as usual and press it. Some boards also have a reset button soldered on the PCB that does the same.

Prefer to copy the file yourself? Copy the `.uf2` from `firmware/build/` to the `RPI-RP2` drive with `cp`. GNOME Files sometimes shows the drive as read-only even though it is not.

### 5. Restore your macros

The keymap is already in the firmware, but macros only live in the backup. With the keyboard plugged in as usual:

```sh
make restore KEYMAP=myname
```

### 6. Keep using VIA

You only need QMK to build and flash the firmware. Day-to-day changes to keys and macros are still made in [VIA](https://usevia.app), with no rebuild.

- `keymap.c` is only the starting layout: the one the keyboard has right after flashing or after its EEPROM is reset. Whatever you change in VIA is stored in the EEPROM and takes precedence over it.
- After significant changes in VIA, save a fresh backup so nothing is lost the next time you flash:

  ```sh
  make backup KEYMAP=myname
  ```

## Layer images

Draw every layer of a VIA backup as an SVG image, with the Sweep's shape:

```sh
make images KEYMAP=myname IMAGES=docs/layers
```

Each key shows what it types. Keys that do something else when held show it underneath (`Alt`, `L1`), and macros show what they do (`Win+L`, `Ctrl+Alt+←`) instead of `M0`. Labels assume a US layout, as VIA does.

Save a fresh backup first with `make backup`, so the images match what the keyboard has now.

## Example: the author's layout

`firmware/keymaps/quique/` holds the author's keymap, and `docs/layers/` its images, both generated from `via-backup.json` in the same folder.

| Layer | Name | |
| --- | --- | --- |
| 0 | Letters | ![Layer 0](docs/layers/layer-0.svg) |
| 1 | Symbols (hold `Space`) | ![Layer 1](docs/layers/layer-1.svg) |
| 2 | Numbers (`TO(2)`) | ![Layer 2](docs/layers/layer-2.svg) |
| 3 | Functions (`TO(3)`) | ![Layer 3](docs/layers/layer-3.svg) |

## Development

```sh
uv venv --python /usr/bin/python3 --system-site-packages
make test
make run
```

| Module | Role |
| --- | --- |
| `layer_watcher` | Turns keyboard reports into layers to display. |
| `layer_report` | Knows the `LY` report format. |
| `keyboard_connection` | Finds the keyboard, asks for its layer, reconnects when unplugged. |
| `hidraw_finder`, `hidraw_keyboard` | Talk to `/dev/hidraw`. |
| `tray_indicator_display`, `layer_icons` | Draw the top bar icon. |
| `via_protocol`, `via_backup`, `keymap_source` | VIA backup, restore and keymap generation. |
| `via_keymap`, `via_macros` | Read the keymap and macros stored in a VIA backup. |
| `keycode_labels` | Turns QMK keycodes into keycap labels. |
| `layer_images`, `layer_drawing`, `sweep_layout` | Draw each layer as an SVG image. |

## License

[MIT](LICENSE). The firmware you build links against QMK, which is GPL-2.0-or-later.
