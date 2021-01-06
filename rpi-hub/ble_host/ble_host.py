from bluepy import btle
import logging


class ScanDelegate(btle.DefaultDelegate):
    def __init__(self, logger):
        btle.DefaultDelegate.__init__(self)
        self.logger = logger

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            status = "new"
        elif isNewData:
            status = "update"
        else:
            status = "old"

        self.logger.debug(f"({status}) {dev.addr} - {dev.addrType} - {dev.rssi} - Connectable: {dev.connectable}")


class BLEHost:
    connected_device = None

    def __init__(self):
        # Configure logger
        self.logger = logging.getLogger(__file__)
        self.logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        streamHandler.setFormatter(formatter)
        self.logger.addHandler(streamHandler)

        # Configure scanner
        self.scanner = btle.Scanner().withDelegate(ScanDelegate(self.logger))

    def scan(self, timeout=2):
        self.logger.info("Scanning...")
        self.devices = self.scanner.scan(timeout)
        return self.devices

    def connect(self, target_address):
        target_address = target_address.lower()
        self.logger.info(f"Connecting to {target_address}...")
        for d in self.devices:
            if d.addr == target_address:
                if d.connectable:
                    self.connected_device = btle.Peripheral(d)
                    self.logger.info(f"Successfully connected to {target_address}")
                    return True
                else:
                    self.logger.info(f"Device {target_address} is not connectable")
                    return False
        
        self.logger.info(f"Device {target_address} not found")
        return False

