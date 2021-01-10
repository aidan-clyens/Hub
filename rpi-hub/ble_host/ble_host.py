from bluepy import btle
import logging


NAME_UUID = btle.UUID("00002a00-0000-1000-8000-00805f9b34fb")


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
                    try:
                        self.connected_device = BLEDevice(self.logger, d)
                        self.logger.info(f"Successfully connected to {self.connected_device.name} ({target_address})")
                        return True
                    except Exception as e:
                        self.logger.warning(str(e))
                        return False
                else:
                    self.logger.info(f"Device {target_address} is not connectable")
                    return False
        
        self.logger.info(f"Device {target_address} not found")
        return False


class BLEDevice:
    def __init__(self, logger, device):
        self.logger = logger
        self.address = device.addr
        self.peripheral = btle.Peripheral(device)

        self._setup_services()
        self.name = self.get_name()

    def __del__(self):
        if self.peripheral:
            self.peripheral.disconnect()

    def get_name(self):
        val = self._read_value(NAME_UUID)
        return val.decode("utf-8")

    def is_connected(self):
        return self._get_state() == "conn"

    def _setup_services(self):
        services = self.peripheral.getServices()
        self.services = {}
        self.characteristics = {}

        self.logger.debug(f"{self.address}: Finding Services...")
        for s in services:
            self.services[s.uuid] = s
            self.logger.debug(f"{s}")
            chars = s.getCharacteristics()
            self.logger.debug(f"{self.address}: Finding Characteristics for service: {s}...")
            for c in chars:
                self.characteristics[c.uuid] = c
                self.logger.debug(f"{c}")

    def _get_state(self):
        state = self.peripheral.getState()
        self.logger.debug(f"{self.name}: State = {state}")
        return state
    
    def _read_value(self, uuid):
        if uuid in self.characteristics.keys():
            c = self.characteristics[uuid]
            if c.supportsRead():
                data = c.read()
                self.logger.debug(f"READ {uuid}: {data} ({len(data)} bytes)")
                return data
            else:
                self.logger.warning(f"{uuid} does not support READ")
        else:
            self.logger.warning(f"Characteristic with UUID {uuid} does not exist")

        return b""


