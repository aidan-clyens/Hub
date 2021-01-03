from gattlib import DiscoveryService, GATTRequester


target_address = "0C:61:CF:A3:09:3E"

name_uuid = "00002a00-0000-1000-8000-00805f9b34fb"


def scan_for_device(address):
    service = DiscoveryService()
    devices = service.discover(2)

    if not address in devices:
        print("Device not found")
        exit()


def connect(address):
    print("Found device. Connecting...")
    requester = GATTRequester(address)

    name = requester.read_by_uuid(name_uuid)[0]
    print("Connected to: ", name.decode())


def main():
    scan_for_device(target_address)
    connect(target_address)

    while True:
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Disconnected")
        exit()
