from gattlib import DiscoveryService, GATTRequester


name_uuid = "00002a00-0000-1000-8000-00805f9b34fb"


class BLEHost:
    logger = None
    discovery_service = None
    requester = None

    def scan(self, target_address, timeout=2):
        if self.logger:
            self.logger.info("Scanning...")
        self.discovery_service = DiscoveryService()
        self.devices = self.discovery_service.discover(timeout)

        if not target_address in self.devices:
            if self.logger:
                self.logger.info(f"Device {target_address} not found")
                return False

        return True

    def connect(self, target_address):
        if self.logger:
            self.logger.info(f"Found device {target_address}. Connecting...")
        self.requester = GATTRequester(target_address)

        name = self.get_name()
        if self.logger:
            self.logger.info(f"Connected to: {name.decode()}")

    def get_name(self):
        if self.requester is None:
            if self.logger:
                self.logger.error("Error. No device is connected")
            return ""
        
        return self.requester.read_by_uuid(name_uuid)[0]

