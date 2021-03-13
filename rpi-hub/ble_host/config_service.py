"""Config Service API

    Usage Example:
        # Variable "device" is an object of type BLEDevice
        # "device" represents a connected BLE peripheral device
        config_service = ConfigService(device)
        config_service.set_rssi_notifications(True, data_queue)
        # ...
        value = config_service.read_rssi()
"""
# Imports
import logging
from bluepy import btle


# Constants
RSSI_UUID = btle.UUID("f000c001-0451-4000-b000-000000000000")


# Class Definitions
class ConfigService:
    """API for the BLE Config Service"""
    def __init__(self, device):
        """Constructor.

        Args:
            device: Connected BLE peripheral device object
        """
        self.device = device

        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def set_rssi_notifications(self, value, data_queue):
        """Enable or disable notifications for RSSI.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable RSSI notifications")
        else:
            self.logger.info("Disable RSSI notifications")

        self.device.set_notifications(RSSI_UUID, value, "rssi", data_queue)

    def read_rssi(self):
        """Read RSSI."""
        value_bytes = self.device.read_value(RSSI_UUID)
        value = -1 * int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read RSSI: {value}")
        return value
