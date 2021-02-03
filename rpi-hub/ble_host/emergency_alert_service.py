"""Emergency Alert Service API

    Usage Example:
        # Variable "device" is an object of type BLEDevice
        # "device" represents a connected BLE peripheral device
        emergency_alert_service = EmergencyAlertService(device)
        emergency_alert_service.set_alert_active_notifications(True, data_queue)
        # ...
        value = emergency_alert_service.read_alert_type()
"""
# Imports
import logging
from bluepy import btle


# Constants
ALERT_TYPE_UUID = btle.UUID("f000b001-0451-4000-b000-000000000000")
ALERT_ACTIVE_UUID = btle.UUID("f000b002-0451-4000-b000-000000000000")


# Class Definitions
class EmergencyAlertService:
    """API for the BLE Emergency Alert Service"""
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

    def set_alert_type_notifications(self, value, data_queue):
        """Enable or disable notifications for alert type.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable Alert Type notifications")
        else:
            self.logger.info("Disable Alert Type notifications")

        self.device.set_notifications(ALERT_TYPE_UUID, value, "alert_type", data_queue)

    def set_alert_active_notifications(self, value, data_queue):
        """Enable or disable notifications for alert active indicator.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable Alert Active notifications")
        else:
            self.logger.info("Disable Alert Active notifications")

        self.device.set_notifications(ALERT_ACTIVE_UUID, value, "alert_active", data_queue)

    def read_alert_type(self):
        """Read alert type."""
        value_bytes = self.device.read_value(ALERT_TYPE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read Alert Type: {value}")
        return value

    def read_alert_active(self):
        """Read alert active_indicator."""
        value_bytes = self.device.read_value(ALERT_ACTIVE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read Alert Active: {value}")
        return value