from gattlib import DiscoveryService, GATTRequester
import logging


name_uuid = "00002a00-0000-1000-8000-00805f9b34fb"


class BLEHost:
    discovery_service = None
    requester = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        streamHandler.setFormatter(formatter)
        self.logger.addHandler(streamHandler)

    def scan(self, target_address, timeout=2):
        self.logger.info("Scanning...")
        self.discovery_service = DiscoveryService("hci0")
        self.devices = self.discovery_service.discover(timeout)

        if not target_address in self.devices:
            self.logger.info(f"Device {target_address} not found")
            return False

        return True

    def connect(self, target_address):
        self.logger.info(f"Found device {target_address}. Connecting...")
        self.requester = GATTRequester(target_address)

        name = self.get_name()
        self.logger.info(f"Connected to: {name.decode()}")
    
    def get_name(self):
        if self.requester is None:
            self.logger.error("Error. No device is connected")
            return ""
        
        return self.requester.read_by_uuid(name_uuid)[0]

