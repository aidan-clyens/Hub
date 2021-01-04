import AWSIoTPythonSDK.MQTTLib as mqtt
import config
import time
import datetime
import logging
import json
import random
import os


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime)):
            return obj.isoformat()


class MQTTClient:
    logger = None
    sequence_num = 0

    def __init__(self, client_id, endpoint, root_path, key_path, cert_path):
        self.client_id = client_id

        self.shadow_client = mqtt.AWSIoTMQTTShadowClient(client_id)

        self.shadow_client.configureEndpoint(endpoint, 8883)
        self.shadow_client.configureCredentials(root_path, key_path, cert_path)

        self.shadow_client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.shadow_client.configureConnectDisconnectTimeout(10)
        self.shadow_client.configureMQTTOperationTimeout(5)

        self.shadow_client.onOnline = self.on_online_callback
        self.shadow_client.onOffline = self.on_offline_callback

        self.client = self.shadow_client.getMQTTConnection()

        self.online = False
    
    def __del__(self):
        self.disconnect()

    def connect(self):
        if not self.online:
            self.shadow_client.connect()
            if self.logger:
                self.logger.info(f"{self.client_id} connected")

    def disconnect(self):
        if self.online:
            self.shadow_client.disconnect()
            if self.logger:
                self.logger.info(f"{self.client_id} disconnected")

    def publish(self, topic, data):
        self.connect()
        if self.online:
            message = {
                "id": self.client_id,
                "sequence": self.sequence_num,
                "data": data,
                "timestamp": datetime.datetime.now()
            }

            try:
                self.client.publish(topic, json.dumps(message, cls=DateTimeEncoder), 1)
                self.sequence_num += 1
                if self.logger:
                    self.logger.info("Published data: " + json.dumps(message, cls=DateTimeEncoder) + " to: " + topic)
            except:
                if self.logger:
                    self.logger.error("Error: Cannot publish message")
        else:
            if self.logger:
                self.logger.error("Not connected. Cannot publish message")

    def on_online_callback(self):
        if self.logger:
            self.logger.info(f"{self.client_id} online")
        self.online = True
    
    def on_offline_callback(self):
        if self.logger:
            self.logger.info(f"{self.client_id} offline")
        self.online = False


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

    # Configure logger
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # Configure MQTT client
    client = MQTTClient(client_id, endpoint, path_to_root, path_to_key, path_to_cert)
    client.logger = logger
    client.connect()

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