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
import logging
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

        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def set_heartrate_notifications(self, value, data_queue):
        """Enable or disable notifications for heart rate value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable Heart Rate Value notifications")
        else:
            self.logger.info("Disable Heart Rate Value notifications")

        self.device.set_notifications(HEARTRATE_VALUE_UUID, value, "heartrate", data_queue)

    def set_spO2_notifications(self, value, data_queue):
        """Enable or disable notifications for SpO2 value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable SpO2 Value notifications")
        else:
            self.logger.info("Disable SpO2 Value notifications")

        self.device.set_notifications(SPO2_VALUE_UUID, value, "spo2", data_queue)

    def set_status_notifications(self, value, data_queue):
        """Enable or disable notifications for sensor status value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable Status notifications")
        else:
            self.logger.info("Disable Status notifications")

        self.device.set_notifications(STATUS_VALUE_UUID, value, "ppg_status", data_queue)

    def set_confidence_notifications(self, value, data_queue):
        """Enable or disable notifications for confidence of reading value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable Reading Confidence notifications")
        else:
            self.logger.info("Disable Reading Confidence notifications")
        self.device.set_notifications(CONFIDENCE_VALUE_UUID, value, "ppg_confidence", data_queue)

    def read_heartrate(self):
        """Read heart rate value."""
        value_bytes = self.device.read_value(HEARTRATE_VALUE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read Heart Rate Value: {value}")
        return value

    def read_spO2(self):
        """Read SpO2 value."""
        value_bytes = self.device.read_value(SPO2_VALUE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read SpO2 Value: {value}")
        return value

    def read_status(self):
        """Read sensor status."""
        value_bytes = self.device.read_value(STATUS_VALUE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        state = "undetected"
        if value == 1:
            state = "off_skin"
        elif value == 2:
            state = "on_subject"
        elif value == 3:
            state = "on_skin"

        self.logger.info(f"Read Status: {state}")
        return state

    def read_confidence(self):
        """Read confidence of sensor reading."""
        value_bytes = self.device.read_value(CONFIDENCE_VALUE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read Reading Confidence: {value}")
        return value
