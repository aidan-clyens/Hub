"""Main Hub device program.

This is the main program for the Hub device. This program connects to BLE peripheral device and listens for data.
When data is received, it is forwarded to the MQTT client to be published to AWS IoT.
This program also simultaneously runs the Alexa Voice Service.
"""

# Imports
import config
import time
import random
import os
import threading
import enum
import queue
from bluepy import btle

from mqtt_client import MQTTClient
from ble_host import BLEHost
from alexa import Alexa


# Constants
SUNLIGHT_VALUE_UUID = btle.UUID("f0002bad-0451-4000-b000-000000000000")


# Global variables
sunlight_value_queue = queue.Queue()


# Class definitions
class BLEState(enum.Enum):
    """BLE connection states."""
    SCANNING = 1
    FOUND_DEVICE = 2
    CONNECTED = 3


# Global functions
def mqtt_function(client, topic):
    """MQTT main thread.

    Args:
        client: Connected MQTT client
        topic: Topic to publish messages to
    """

    # Main loop
    while True:
        value = sunlight_value_queue.get(block=True)
        client.publish(topic, int.from_bytes(value, byteorder="little"))


def ble_function(ble, device_address):
    """BLE main thread.

    Args:
        ble: BLE host to scan for devices
        device_address: Target BLE device MAC address
    """

    heartbeat = 30
    device = None

    ble_state = BLEState.SCANNING

    # Main loop
    while True:
        if ble_state == BLEState.SCANNING:
            devices = ble.scan(5.0)
            connected = ble.connect(device_address)
            if connected:
                ble_state = BLEState.FOUND_DEVICE

        elif ble_state == BLEState.FOUND_DEVICE:
            device = ble.connected_device
            device.set_notifications(SUNLIGHT_VALUE_UUID, True, sunlight_value_queue)

            ble_state = BLEState.CONNECTED

        elif ble_state == BLEState.CONNECTED:
            try:
                if device.wait_for_notifications(heartbeat):
                    continue
            except btle.BTLEDisconnectError:
                ble_state = BLEState.SCANNING


def alexa_function(alexa):
    """Alexa main thread.

    Args:
        alexa: Alexa application wrapper
    """

    alexa.start()


def main():
    """Main."""

    # Check for AWS IoT certificates
    if not os.path.exists(config.path_to_cert) or \
        not os.path.exists(config.path_to_key) or \
        not os.path.exists(config.path_to_root):
        print("Error: Certificate files do not exist. Please get them from AWS and edit config.py.")
        exit()

    endpoint = config.endpoint
    client_id = config.client_id
    path_to_cert = config.path_to_cert
    path_to_key = config.path_to_key
    path_to_root = config.path_to_root
    topic = config.topic

    device_address = config.device_address

    # Configure MQTT client
    client = MQTTClient(client_id, endpoint, path_to_root, path_to_key, path_to_cert)
    client.connect()

    # Configure BLE host and connect to peripheral device
    ble = BLEHost()

    # Configure Alexa
    alexa = Alexa()

    # Create and start threads
    mqtt_thread = threading.Thread(target=mqtt_function, args=(client, topic), daemon=True)
    ble_thread = threading.Thread(target=ble_function, args=(ble, device_address), daemon=True)
    alexa_thread = threading.Thread(target=alexa_function, args=(alexa, ), daemon=True)

    mqtt_thread.start()
    ble_thread.start()
    alexa_thread.start()

    # Wait until threads exit
    mqtt_thread.join()
    ble_thread.join()
    alexa_thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
