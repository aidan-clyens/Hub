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

from rpihub.logger import get_logger


# Constants
HEARTRATE_VALUE_UUID = btle.UUID("f000a001-0451-4000-b000-000000000000")
HEARTRATE_CONFIDENCE_UUID = btle.UUID("f000a002-0451-4000-b000-000000000000")
SPO2_VALUE_UUID = btle.UUID("f000a003-0451-4000-b000-000000000000")
SPO2_CONFIDENCE_UUID = btle.UUID("f000a004-0451-4000-b000-000000000000")
SCD_STATE_VALUE_UUID = btle.UUID("f000a005-0451-4000-b000-000000000000")


# Class Definitions
class HeartRateService:
    """API for the BLE Heart Rate Service"""
    def __init__(self, device, log_level):
        """Constructor.

        Args:
            device: Connected BLE peripheral device object
        """
        self.device = device

        # Configure logger
        self.logger = get_logger(__name__, log_level)

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

    def set_heartrate_confidence_notifications(self, value, data_queue):
        """Enable or disable notifications for heart rate confidence.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable Heart Rate Confidence notifications")
        else:
            self.logger.info("Disable Heart Rate Confidence notifications")

        self.device.set_notifications(HEARTRATE_CONFIDENCE_UUID, value, "heartrate_confidence", data_queue)

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

    def set_spO2_confidence_notifications(self, value, data_queue):
        """Enable or disable notifications for SpO2 confidence.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable SpO2 Confidence notifications")
        else:
            self.logger.info("Disable SpO2 Confidence notifications")

        self.device.set_notifications(SPO2_CONFIDENCE_UUID, value, "spo2_confidence", data_queue)

    def set_scd_state_notifications(self, value, data_queue):
        """Enable or disable notifications for sensor SCD state value.

        Args:
            value: Boolean indicating enable or disable
            data_queue: A queue to store data received
        """
        if value:
            self.logger.info("Enable SCD State notifications")
        else:
            self.logger.info("Disable SCD State notifications")

        self.device.set_notifications(SCD_STATE_VALUE_UUID, value, "scd_state", data_queue)

    def read_heartrate(self):
        """Read heart rate value."""
        value_bytes = self.device.read_value(HEARTRATE_VALUE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read Heart Rate Value: {value}")
        return value

    def read_heartrate_confidence(self):
        """Read heart rate confidence."""
        value_bytes = self.device.read_value(HEARTRATE_CONFIDENCE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read Heart Rate Confidence: {value}")
        return value

    def read_spO2(self):
        """Read SpO2 value."""
        value_bytes = self.device.read_value(SPO2_VALUE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read SpO2 Value: {value}")
        return value

    def read_spO2_confidence(self):
        """Read SpO2 confidence."""
        value_bytes = self.device.read_value(SPO2_CONFIDENCE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        self.logger.info(f"Read SpO2 Confidence: {value}")
        return value

    def read_scd_state(self):
        """Read sensor SCD state."""
        value_bytes = self.device.read_value(SCD_STATE_VALUE_UUID)
        value = int.from_bytes(value_bytes, byteorder="little")
        state = "undetected"
        if value == 1:
            state = "off_skin"
        elif value == 2:
            state = "on_subject"
        elif value == 3:
            state = "on_skin"

        self.logger.info(f"Read SCD State: {state}")
        return state
