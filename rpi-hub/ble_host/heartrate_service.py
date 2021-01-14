"""HeartRate Service API

    Usage Example:
        # Variable "device" is an object of type BLEDevice
        # "device" represents a connected BLE peripheral device
        heartrate_service = HeartRateService(device)
        heartrate_service.set_heartrate_notifications(True, data_queue)
        # ...
        value = heartrate_service.read_heartrate()
"""
# Imports
from bluepy import btle

# Constants
HEARTRATE_VALUE_UUID = btle.UUID("f000a001-0451-4000-b000-000000000000")
SPO2_VALUE_UUID = btle.UUID("f000a002-0451-4000-b000-000000000000")
STATUS_VALUE_UUID = btle.UUID("f000a003-0451-4000-b000-000000000000")
CONFIDENCE_VALUE_UUID = btle.UUID("f000a004-0451-4000-b000-000000000000")

# Class Definitions
class HeartRateService:
    """API for the BLE Heart Rate Service"""
    def __init__(self, device):
        """Constructor.

        Args:
            device: Connected BLE peripheral device object
        """
        self.device = device

    def set_heartrate_notifications(self, value, data_queue):
        """Enable or disable notifications for heart rate value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        self.device.set_notifications(HEARTRATE_VALUE_UUID, value, data_queue)

    def set_spO2_notifications(self, value, data_queue):
        """Enable or disable notifications for SpO2 value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        self.device.set_notifications(SPO2_VALUE_UUID, value, data_queue)

    def set_status_notifications(self, value, data_queue):
        """Enable or disable notifications for sensor status value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        self.device.set_notifications(STATUS_VALUE_UUID, value, data_queue)

    def set_confidence_notifications(self, value, data_queue):
        """Enable or disable notifications for confidence of reading value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        self.device.set_notifications(CONFIDENCE_VALUE_UUID, value, data_queue)

    def read_heartrate(self):
        """Read heart rate value."""
        value_bytes = self.device.read_value(HEARTRATE_VALUE_UUID)
        return int.from_bytes(value_bytes, byteorder="little")

    def read_spO2(self):
        """Read SpO2 value."""
        value_bytes = self.device.read_value(SPO2_VALUE_UUID)
        return int.from_bytes(value_bytes, byteorder="little")

    def read_status(self):
        """Read sensor status."""
        value_bytes = self.device.read_value(STATUS_VALUE_UUID)
        return int.from_bytes(value_bytes, byteorder="little")

    def read_confidence(self):
        """Read confidence of sensor reading."""
        value_bytes = self.device.read_value(CONFIDENCE_VALUE_UUID)
        return int.from_bytes(value_bytes, byteorder="little")
