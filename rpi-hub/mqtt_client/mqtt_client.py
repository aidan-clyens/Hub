"""MQTT Client class

    Usage Example:
        client = MQTTClient(client_id, endpoint, root_path, key_path, cert_path)
        client.connect()
        client.publish("ExampleTopic", 10)
"""

# Imports
import datetime
import json
import logging
import AWSIoTPythonSDK.MQTTLib as mqtt


# Class definitions
class DateTimeEncoder(json.JSONEncoder):
    """Encode datetime."""
    def default(self, obj):
        """Encode datetime."""
        if isinstance(obj, (datetime.datetime)):
            return obj.isoformat()


class MQTTClient:
    """MQTT client to connect to AWS IoT server."""
    sequence_num = 0

    def __init__(self, client_id, endpoint, root_path, key_path, cert_path):
        """Constructor.

        Args:
            client_id: Name this of AWS IoT client.
            endpoint: Endpoint for AWS IoT server.
            root_path: Path to root file.
            key_path: Path to key file.
            cert_path: Path to cert file.
        """
        self.client_id = client_id

        # Configure logger
        self.logger = logging.getLogger("AWSIoTPythonSDK.core")
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # Configure MQTT shadow client
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
        """Destructor."""
        self.disconnect()

    def connect(self):
        """Connect to AWS IoT server."""
        if not self.online:
            self.shadow_client.connect()
            self.logger.info(f"{self.client_id} connected")

    def disconnect(self):
        """Disconnect from AWS IoT server."""
        if self.online:
            self.shadow_client.disconnect()
            self.logger.info(f"{self.client_id} disconnected")

    def publish(self, topic, data):
        """Publish data to an AWS IoT topic."""
        self.connect()
        if self.online:
            message = {
                "hub_id": self.client_id,
                "sequence": self.sequence_num,
                "timestamp": datetime.datetime.now()
            }

            # Add data to packet
            for [key, value] in data.items():
                message[key] = value

            try:
                self.client.publish(topic, json.dumps(message, cls=DateTimeEncoder), 1)
                self.sequence_num += 1
                self.logger.info("Published data: " + json.dumps(message, cls=DateTimeEncoder) + " to: " + topic)
            except:
                self.logger.error("Error: Cannot publish message")
        else:
            self.logger.error("Not connected. Cannot publish message")

    def on_online_callback(self):
        """Callback for when MQTT client goes online."""
        self.logger.debug(f"{self.client_id} online")
        self.online = True

    def on_offline_callback(self):
        """Callback for when MQTT client goes offline."""
        self.logger.debug(f"{self.client_id} offline")
        self.online = False
