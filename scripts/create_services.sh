#!/bin/bash
user_services_dir=~/".config/systemd/user"
app_dir="$(dirname "$(dirname "$(realpath $0)")")"

if [ $EUID -eq 0 ]; then
    echo "Run without root privileges"
    exit 1
fi

echo "Enable user lingering"
loginctl enable-linger "$(logname)"

echo "Creating directory for services under current user"
mkdir -p $user_services_dir

echo "Add Zeroconf Service"
cat <<EOF >$user_services_dir/zeroconf-service.service
[Unit]
Description=Zeroconf Service
After=network-online.target
Wants=network-online.target

[Service]
Restart=always
TimeoutStopSec=5s
ExecStart=$app_dir/venv/bin/python $app_dir/src/main.py

[Install]
WantedBy=default.target
EOF

echo Done
