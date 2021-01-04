from mqtt_client import MQTTClient
from ble_host import BLEHost

import config
import time
import random
import os
import threading


def mqtt_function(client, topic):
    interval = 5 * 60

    # Main loop
    while True:
        data = random.uniform(0, 20)
        client.publish(topic, data)
        time.sleep(interval)


def ble_function(ble, device_address):
    while not ble.scan(device_address):
        pass
    ble.connect(device_address)

    # Main loop
    while True:
        pass


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

    # Create and start threads
    mqtt_thread = threading.Thread(target=mqtt_function, args=(client, topic), daemon=True)
    ble_thread = threading.Thread(target=ble_function, args=(ble, device_address), daemon=True)

    mqtt_thread.start()
    ble_thread.start()

    # Wait until threads exit
    mqtt_thread.join()
    ble_thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
