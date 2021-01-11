from bluepy import btle


SUNLIGHT_VALUE_UUID = btle.UUID("f0002bad-0451-4000-b000-000000000000")


class SunlightService:
    def __init__(self, device):
        self.device = device

    def set_notifications(self, value):
        self.device.set_notifications(SUNLIGHT_VALUE_UUID, True)

    def read_sunlight_value(self):
        data = self.device.read_value(SUNLIGHT_VALUE_UUID)
        return int.from_bytes(data, byteorder="little")
