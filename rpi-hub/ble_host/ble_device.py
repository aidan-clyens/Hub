"""BLE Device and NotificationDelegate class

    Usage Example:
        device = BLEDevice(logger, bluepy_device)
        device.set_notifications(EXAMPLE_UUID, True)

        while True:
            if device.wait_for_notifications(30.0):
                data = device.read_value(EXAMPLE_UUID)
                continue
"""
#Imports
from bluepy import btle


# Constants
NAME_UUID = btle.UUID("00002a00-0000-1000-8000-00805f9b34fb")


# Class definitions
class NotificationDelegate(btle.DefaultDelegate):
    """Callback for Notifications received."""
    def __init__(self, logger, handle, message_queue):
        """Constructor.

        Args:
            logger: Logger for BLE host and device.
            handle: Handle of Characteristic to receive notifications from.
            message_queue: Message queue for incoming data.
        """
        btle.DefaultDelegate.__init__(self)
        self.logger = logger
        self.handle = handle
        self.message_queue = message_queue

    def handleNotification(self, handle, data):
        """Handler for notifications.

        Args:
            handle: Handle of Characteristic notification is received from.
            data: Data received from Characteristic notification is received from.
        """
        if handle == self.handle:
            self.logger.debug(f"Notification: {handle}, {data}")
            self.message_queue.put(data)


class BLEDevice:
    """BLE Device."""

    def __init__(self, logger, device):
        """Constructor.

        Args:
            logger: Logger for BLE host.
            device: BLE device object from bluepy.btle package.
        """
        self.logger = logger
        self.address = device.addr
        self.peripheral = btle.Peripheral(device)

        self.setup_services()
        self.name = self.get_name()

    def __del__(self):
        """Destructor."""
        if self.peripheral:
            self.peripheral.disconnect()

    def get_name(self):
        """Get name of BLE device."""
        val = self.read_value(NAME_UUID)
        return val.decode("utf-8")

    def wait_for_notifications(self, timeout=1):
        """Block for notifications from BLE device.

        Args:
            timeout: Blocking timeout in seconds.

        Returns:
            Boolean indicating notification has been received.
        """
        return self.peripheral.waitForNotifications(timeout)

    def is_connected(self):
        """Returns whether BLE device is connected."""
        return self.get_state() == "conn"

    def setup_services(self):
        """Setup and cache BLE Services and Characteristics from device."""
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
                self.logger.debug(f"{c.propertiesToString()}")

    def set_notifications(self, uuid, value, message_queue):
        """Enable or disable notifications for a Characteristic.

        Args:
            uuid: UUID of Characteristic.
            value: Boolean value to enable or disable notifications.
            message_queue: Message queue for incoming data.
        """
        if uuid in self.characteristics.keys():
            c = self.characteristics[uuid]
            if "notify" in c.propertiesToString().lower():
                self.peripheral.setDelegate(NotificationDelegate(self.logger, c.getHandle(), message_queue))

                handle = c.getHandle() + 1
                if value:
                    value_bytes = b"\x01\x00"
                else:
                    value_bytes = b"\x00\x00"

                self.peripheral.writeCharacteristic(handle, value_bytes, withResponse=True)
                self.logger.debug(f"Set notifications for {self.characteristics[uuid]} to {value}")
            else:
                self.logger.warning(f"Notifications disabled for {self.characteristics[uuid]}")
        else:
            self.logger.warning(f"Characteristic with UUID {uuid} does not exist")

    def get_state(self):
        """Get connection state of BLE device."""
        try:
            state = self.peripheral.getState()
        except Exception as e:
            self.logger.warning(f"Error getting state: {e}")
            state = "conn"

        self.logger.debug(f"{self.name}: State = {state}")
        return state

    def read_value(self, uuid):
        """Read value of Characteristic.

        Args:
            uuid: UUID of Characteristic to read.

        Returns:
            Value of Characteristic in bytes.
        """
        if uuid in self.characteristics.keys():
            c = self.characteristics[uuid]
            if c.supportsRead():
                data = c.read()
                self.logger.debug(f"READ {self.characteristics[uuid]}: {data} ({len(data)} bytes)")
                return data

            self.logger.warning(f"{self.characteristics[uuid]} does not support READ")
        else:
            self.logger.warning(f"Characteristic with UUID {uuid} does not exist")

        return b""
    
    def write_value(self, uuid, data):
        """Write value to Characteristic.

        Args:
            uuid: UUID of Characteristic to write to.
            data: Data to write to Characteristic in bytes.
        """
        if uuid in self.characteristics.keys():
            c = self.characteristics[uuid]
            c.write(data)
            self.logger.debug(f"WRITE {self.characteristics[uuid]}: {data} ({len(data)} bytes)")
        else:
            self.logger.warning(f"Characteristic with UUID {uuid} does not exist")
