# Zeroconf Service

A configurable Zeroconf service registration with auto updates at specified intervals.

## Installation

Download project

```bash
git clone https://github.com/evgenii-d/zeroconf-service.git
```

Execute `setup_project.sh`

```bash
chmod +x ./scripts/setup_project.sh && ./scripts/setup_project.sh
```

Run app

```bash
./venv/bin/python -m src.main
```

(Optional) Create and enable a Systemd User Service

```bash
chmod +x ./scripts/install_service.sh && ./scripts/install_service.sh
```

### `config.json` example

```json
{
    "type": "_http._tcp.local.",
    "name": "my-service._http._tcp.local.",
    "port": 8080,
    "properties": {
        "description": "My Zeroconf Service"
    },
    "interval": 60
}
```
