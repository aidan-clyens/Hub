from gattlib import DiscoveryService, GATTRequester


device_address = "0C:61:CF:A3:09:3E"

name_uuid = "00002a00-0000-1000-8000-00805f9b34fb"


class BLEHost:
    discovery_service = None
    requester = None

    def scan(self, target_address, timeout=2):
        self.discovery_service = DiscoveryService()
        self.devices = self.discovery_service.discover(timeout)

        if not target_address in self.devices:
            print(f"Device {target_address} not found")
            exit()

    def connect(self, target_address):
        print(f"Found device {target_address}. Connecting...")
        self.requester = GATTRequester(target_address)

        name = self.get_name()
        print("Connected to: ", name.decode())

    def get_name(self):
        if self.requester is None:
            print("Error. No device is connected")
            return ""
        
        return self.requester.read_by_uuid(name_uuid)[0]


def main():
    ble = BLEHost()
    ble.scan(device_address)
    ble.connect(device_address)

    while True:
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Disconnected")
        exit()
