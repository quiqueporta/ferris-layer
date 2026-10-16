#!/bin/sh
# Installs ferris-layer for the current user: system packages, virtualenv, udev rule, config and systemd service.
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
SYSTEM_PACKAGES="python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator librsvg2-common"

step() {
    printf '\n==> %s\n' "$1"
}

step "Checking system packages"
missing=""
for package in $SYSTEM_PACKAGES; do
    dpkg -s "$package" >/dev/null 2>&1 || missing="$missing $package"
done
if [ -n "$missing" ]; then
    sudo apt-get install -y $missing
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi

# GTK and AppIndicator bindings come from apt, so the virtualenv uses the system Python and sees its packages.
step "Creating the virtualenv"
uv venv --python /usr/bin/python3 --system-site-packages --allow-existing "$HERE/.venv"
uv sync --project "$HERE" --no-dev

step "Installing the udev rule (needs sudo)"
sudo install -m 644 "$HERE/udev/70-ferris-sweep.rules" /etc/udev/rules.d/
sudo udevadm control --reload
sudo udevadm trigger --subsystem-match=hidraw

step "Installing the config"
mkdir -p "$CONFIG_HOME/ferris-layer"
if [ ! -f "$CONFIG_HOME/ferris-layer/config.toml" ]; then
    cp "$HERE/config.example.toml" "$CONFIG_HOME/ferris-layer/config.toml"
fi

step "Installing the systemd user service"
mkdir -p "$CONFIG_HOME/systemd/user"
sed "s|@EXEC@|$HERE/.venv/bin/ferris-layer|" "$HERE/systemd/ferris-layer.service.in" \
    > "$CONFIG_HOME/systemd/user/ferris-layer.service"
systemctl --user daemon-reload
systemctl --user enable --now ferris-layer.service

step "Done. Edit $CONFIG_HOME/ferris-layer/config.toml to name your layers."
