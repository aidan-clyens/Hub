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
from ble_host import BLEHost, HeartRateService
from alexa import Alexa


# Global variables
message_queue = queue.Queue()


# Class definitions
class BLEState(enum.Enum):
    """BLE connection states."""
    SCANNING = 1
    FOUND_DEVICE = 2
    CONNECTED = 3


class MqttMessage:
    def __init__(self, topic, data):
        self.topic = topic
        self.data = data


# Global functions
def mqtt_function(client):
    """MQTT main thread.

    Args:
        client: Connected MQTT client
    """

    # Main loop
    while True:
        message = message_queue.get()
        client.publish(message.topic, message.data)


def ble_function(ble, device_address, topics):
    """BLE main thread.

    Args:
        ble: BLE host to scan for devices
        device_address: Target BLE device MAC address
    """

    polling_interval = 5
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
            heartrate_service = HeartRateService(device)

            # Alert AWS when new wristband is connected
            wristband_id = "Test" # TODO: Get device ID
            message = MqttMessage(topics["wristband_connect"], {"wristband_id": wristband_id, "mac_address": device_address})
            message_queue.put(message)

            ble_state = BLEState.CONNECTED

        elif ble_state == BLEState.CONNECTED:
            # Read heart rate data periodically
            try:
                # TODO: Wait for emergency alert notifications
                if device.wait_for_notifications(polling_interval):
                    # TODO: Handle notifications
                    pass

                data = {}

                data["wristband_id"] = "Test" # TODO
                data["rssi"] = 0 # TODO
                data["heartrate"] = heartrate_service.read_heartrate()
                data["heartrate_confidence"] = heartrate_service.read_heartrate_confidence();
                data["spO2"] = heartrate_service.read_spO2()
                data["spO2_confidence"] = heartrate_service.read_spO2_confidence();
                data["contact_status"] = heartrate_service.read_scd_state()

                message = MqttMessage(topics["data"], data)
                message_queue.put(message)
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

    topics = {
        "hub_connect": config.hub_connect_topic,    
        "wristband_connect": config.wristband_connect_topic,    
        "data": config.data_topic,    
        "alert": config.alert_topic
    }

    device_address = config.device_address

    # Configure MQTT client
    client = MQTTClient(client_id, endpoint, path_to_root, path_to_key, path_to_cert)
    client.connect()

    # Alert AWS of new Hub connection
    message_queue.put(MqttMessage(topics["hub_connect"], {}))

    # Configure BLE host and connect to peripheral device
    ble = BLEHost()

    # Configure Alexa
    alexa = Alexa()

    # Create and start threads
    mqtt_thread = threading.Thread(target=mqtt_function, args=(client, ), daemon=True)
    ble_thread = threading.Thread(target=ble_function, args=(ble, device_address, topics), daemon=True)
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
