from mqtt_client import MQTTClient
from ble_host import BLEHost

import config
import time
import random
import os


def main():
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

    while not ble.scan(device_address):
        pass

    ble.connect(device_address)

    interval = 5 * 60
    while True:
        data = random.uniform(0, 20)

        client.publish(topic, data)

        time.sleep(interval)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
