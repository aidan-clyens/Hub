"""BLE Host and ScanDelegate classes.

    Usage Example:

    host = BLEHost()
    devices_list = host.scan(5.0)
    is_connected = host.connect(ff:ff:ff:ff:ff:ff)
"""

# Imports
import logging
import os
from bluepy import btle

from .ble_device import BLEDevice


# Class definitions
class ScanDelegate(btle.DefaultDelegate):
    """Callback for BLE scanning results."""

    def __init__(self, logger):
        """Constructor

        Args:
            logger: Logger used by the BLE host
        """
        btle.DefaultDelegate.__init__(self)
        self.logger = logger

    def handleDiscovery(self, dev, isNewDev, isNewData):
        """Handle discovery of new BLE device.

        Args:
            dev: BLE device object.
            isNewDev: A boolean indicating whether device is new or not.
            isNewData: A boolean indicating whether data is new or not.
        """
        if isNewDev:
            status = "new"
        elif isNewData:
            status = "update"
        else:
            status = "old"

        self.logger.debug(f"({status}) {dev.addr} - {dev.addrType} - {dev.rssi} - Connectable: {dev.connectable}")


class BLEHost:
    """BLE host and scanner"""
    connected_device = None

    def __init__(self):
        """Constructor."""
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # Configure scanner
        self.scanner = btle.Scanner().withDelegate(ScanDelegate(self.logger))

        self.cached_devices = {}

    def scan(self, timeout=2):
        """Scan for BLE devices.

        Args:
            timeout: Timeout value for scanning in seconds.

        Returns:
            List of BLE device objects scanned.
        """
        self.logger.info("Scanning...")
        self.devices = self.scanner.scan(timeout)
        return self.devices

    def connect(self, target_address):
        """Connect to a target BLE device if it is found.

        Args:
            target_address: MAC address of target BLE device.

        Returns:
            Boolean indicating whether device was successfully connected to.
        """
        target_address = target_address.lower()
        self.logger.info(f"Connecting to {target_address}...")
        for d in self.devices:
            if d.addr == target_address:
                if d.connectable:
                    try:
                        if d.addr not in self.cached_devices.keys():
                            self.logger.debug(f"Caching device: {d.addr}")
                            self.cached_devices[d.addr] = BLEDevice(d)
                        else:
                            self.logger.debug(f"Found cached device: {d.addr}")
                            self.cached_devices[d.addr].connect()

                        self.connected_device = self.cached_devices[d.addr]
                        self.logger.info(f"Successfully connected to {self.connected_device.name} ({target_address})")
                        return True
                    except Exception as e:
                        self.logger.error(f"Error connecting to device: {str(e)}")
                        os._exit(1)
                else:
                    self.logger.info(f"Device {target_address} is not connectable")
                    return False

        self.logger.info(f"Device {target_address} not found")
        return False
