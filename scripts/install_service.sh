#!/bin/bash
user_services_dir="$HOME/.config/systemd/user"
app_dir="$(dirname "$(dirname "$(realpath "$0")")")"

# Check for root privileges
if [ "$EUID" -eq 0 ]; then
    echo "Run script without root privileges" >&2
    exit 1
fi

echo "[Install Service]"

echo
echo "> Enabling user lingering"
loginctl enable-linger "$(logname)"

echo "> Creating directory for user services"
mkdir -p "$user_services_dir"

echo "> Creating Zeroconf service"
cat <<EOF >"$user_services_dir/zeroconf.service"
[Unit]
Description=Zeroconf Service
After=network-online.target
Wants=network-online.target

[Service]
Restart=always
TimeoutStopSec=10s
ExecStart=$app_dir/venv/bin/python $app_dir/src/main.py

[Install]
WantedBy=default.target
EOF

echo "> Enabling the Zeroconf service"
systemctl --user enable zeroconf.service

echo
echo Done
