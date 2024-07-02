# Zeroconf Service

Configurable Zeroconf service registration with automatic service updates at specified intervals.

Example `config.json`:

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
