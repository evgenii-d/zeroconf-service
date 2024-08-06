"""Zeroconf service with interval updates."""
import json
import socket
import logging
from time import sleep
from signal import signal, SIGTERM, SIGINT
from pathlib import Path
from threading import Event, Thread
from dataclasses import asdict, dataclass, field
from zeroconf import ServiceInfo, Zeroconf

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for the Zeroconf service."""
    type: str = "_http._tcp.local."
    name: str = f"{socket.gethostname()}._http._tcp.local."
    port: int = 8080
    properties: dict = field(default_factory=dict)
    interval: float = 60


class ZeroconfService:
    """Manage a Zeroconf service registration and updates."""

    def __init__(self, info: ServiceInfo, interval: float = 60) -> None:
        """Initializes ZeroconfService.

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

    def _service_loop(self) -> None:
        """Continuously update the service registration."""
        while not self._stop_event.is_set():
            logger.info("Update service registration")
            self._zeroconf.unregister_service(self._info)
            self._zeroconf.register_service(self._info)
            self._stop_event.wait(self._update_interval)
        self._zeroconf.unregister_service(self._info)

    def start(self) -> None:
        """Start the Zeroconf service registration."""
        if self._thread.is_alive():
            logger.info("Service already started")
            return
        logger.info("Starting Zeroconf service")
        self._thread.start()

    def stop(self) -> None:
        """Stop the Zeroconf service."""
        logger.info("Stopping service...")
        self._stop_event.set()
        self._thread.join()
        logger.info("Service stopped")

    def close(self) -> None:
        """Stop the service and close the Zeroconf instance."""
        self.stop()
        self._zeroconf.close()
        logger.info("Zeroconf closed")

    def is_alive(self) -> bool:
        """Checks if the service is running."""
        return self._thread.is_alive()


def load_config(config_path: Path) -> ServiceConfig:
    """
    Load service configuration from a JSON file
    or create a default configuration if the file is not found.

    Args:
        config_path (Path): Path to the JSON configuration file.

    Returns:
        ServiceConfig: 
            A ServiceConfig object with the loaded configuration.
    """
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


def main() -> None:
    """Main function to run the Zeroconf service."""
    log_format = "[%(levelname)s] %(module)s: %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    config = load_config(Path(__file__).parent/"config.json")
    hostname = socket.gethostname()
    # Use hostname in the name if not explicitly specified in config
    config.name = config.name if config.name else f"{hostname}.{config.type}"
    service_info = ServiceInfo(
        type_=config.type,
        name=config.name,
        port=config.port,
        properties=config.properties,
        server=f"{hostname}.local.",
    )

    zeroconf_service = ZeroconfService(service_info, config.interval)
    signal(SIGINT, lambda _, __: zeroconf_service.close())
    signal(SIGTERM, lambda _, __: zeroconf_service.close())
    zeroconf_service.start()

    while zeroconf_service.is_alive():
        sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
