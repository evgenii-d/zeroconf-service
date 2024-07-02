"""Manages and registers a Zeroconf service with configurable settings."""
import json
import signal
import socket
import atexit
import logging
from time import sleep
from pathlib import Path
from threading import Event, Thread
from dataclasses import asdict, dataclass, field
from zeroconf import ServiceInfo, Zeroconf

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration data for the Zeroconf service."""
    type: str = "_http._tcp.local."
    name: str = f"{socket.gethostname()}._http._tcp.local."
    port: int = 8080
    properties: dict = field(default_factory=dict)
    interval: float = 60


class ZeroconfService:
    """Manages registration and updates for a Zeroconf service."""

    def __init__(self, info: ServiceInfo, interval: float = 60) -> None:
        """Initializes ZeroconfService

        Args:
            info (ServiceInfo):
                Zeroconf service information.
            interval (float, optional):
                Update interval. Defaults to 60.
        """
        self._info = info
        self._update_interval = interval
        self._zeroconf = Zeroconf()
        self._stop_event = Event()
        self._thread = Thread(target=self._service_loop, daemon=True)

    def update_info(self, info: ServiceInfo) -> None:
        """Updates the service information."""
        self._info = info

    def register(self) -> None:
        """Registers the service with Zeroconf."""
        self._zeroconf.register_service(self._info)

    def unregister(self) -> None:
        """Unregisters the service from Zeroconf."""
        self._zeroconf.unregister_service(self._info)

    def _service_loop(self) -> None:
        """Periodically updates the service registration."""
        while not self._stop_event.is_set():
            logger.info("Update service registration")
            self.unregister()
            self.register()
            self._stop_event.wait(self._update_interval)

    def start(self) -> None:
        """Starts the Zeroconf service in a separate thread."""
        if self._thread.is_alive():
            logger.info("Service already started")
            return
        logger.info("Starting Zeroconf service")
        self._thread.start()

    def stop(self) -> None:
        """Stops the Zeroconf service and unregisters it."""
        logger.info("Stopping service...")
        self._stop_event.set()
        self._thread.join()
        self.unregister()
        logger.info("Service stopped")

    def is_alive(self) -> bool:
        """Checks if the service thread is running."""
        return self._thread.is_alive()


def load_config(config_path: Path) -> ServiceConfig:
    """Loads service configuration from a JSON file."""
    try:
        config_data = config_path.read_text("utf-8")
        config = ServiceConfig(**json.loads(config_data))
    except FileNotFoundError:
        config = ServiceConfig()
        config_data = json.dumps(asdict(config), indent=4)
        config_path.write_text(config_data, "utf-8")
        logger.warning("Config file not found. Created default config.")
    except (TypeError, json.JSONDecodeError):
        config = ServiceConfig()
        logger.warning("Invalid JSON in config file. Using defaults.")
    return config


def main():
    """Configures and starts the Zeroconf service."""
    log_format = "[%(levelname)s] %(module)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    config = load_config(Path(__file__).parent/"config.json")
    hostname = socket.gethostname()
    config.name = config.name if config.name else f"{hostname}.{config.type}"
    service_info = ServiceInfo(
        type_=config.type,
        name=config.name,
        port=config.port,
        properties=config.properties,
        server=f"{hostname}.local.",
    )

    zeroconf_service = ZeroconfService(service_info, config.interval)
    atexit.register(zeroconf_service.stop)
    signal.signal(signal.SIGTERM, lambda _, __: zeroconf_service.stop())
    signal.signal(signal.SIGINT, lambda _, __: zeroconf_service.stop())
    zeroconf_service.start()

    while zeroconf_service.is_alive():
        sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
