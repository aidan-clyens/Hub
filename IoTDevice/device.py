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

def main():
    client.connect()
    i = 0
    data = 12.5
    while True:
        message = {
            "id": client_id,
            "sequence": i,
            "data": data,
            "timestamp": datetime.datetime.now()
        }

        print("Published message: " + json.dumps(message, cls=DateTimeEncoder) + " to: " + topic)
        client.publish(topic, json.dumps(message, cls=DateTimeEncoder), 1)

        time.sleep(5)


if __name__ == '__main__':
    try:
        main()
    except:
        print("Exiting")
        client.disconnect()
