import AWSIoTPythonSDK.MQTTLib as mqtt
import config
import time
import datetime
import logging
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime)):
            return obj.isoformat()


endpoint = config.endpoint
client_id = config.client_id
path_to_cert = config.path_to_cert
path_to_key = config.path_to_key
path_to_root = config.path_to_root
topic = config.topic


logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


client = mqtt.AWSIoTMQTTClient(client_id)
client.configureEndpoint(endpoint, 8883)
client.configureCredentials(path_to_root, path_to_key, path_to_cert)

client.configureAutoReconnectBackoffTime(1, 32, 20)
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)


client.connect()
i = 0
data = 12.5
while True:
    try:
        message = {
            "id": client_id,
            "sequence": i,
            "data": data,
            "timestamp": datetime.datetime.now()
        }

        logger.info("Publishing message: " + json.dumps(message, cls=DateTimeEncoder) + " to: " + topic)
        client.publish(topic, json.dumps(message, cls=DateTimeEncoder), 1)

        i += 1
        time.sleep(10)
    except KeyboardInterrupt:
        exit()
    except:
        logger.error("Lost connection, attempting retry")
