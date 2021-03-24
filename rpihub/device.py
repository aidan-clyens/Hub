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
import sys
import threading
import enum
import queue
import logging
import argparse
from bluepy import btle

from mqtt_client import MQTTClient
from ble_host import BLEHost, ConfigService, HeartRateService, EmergencyAlertService
from alexa import VoiceEngine


# Constants
LOW_HEARTRATE = 60
HIGH_HEARTRATE = 110


# Global variables
message_queue = queue.Queue()
voice_engine_queue = queue.Queue()

rssi_data_queue = queue.Queue()
alert_data_queue = queue.Queue()
heartrate_data_queue = queue.Queue()
heartrate_confidence_data_queue = queue.Queue()
spO2_data_queue = queue.Queue()
scd_data_queue = queue.Queue()


# Class definitions
class BLEState(enum.Enum):
    """BLE connection states."""
    SCANNING = 1
    FOUND_DEVICE = 2
    CONNECTED = 3
    DISCONNECTED = 4


class HubState(enum.Enum):
    """Hub activity states."""
    POLLING = 1
    READ_DATA = 2


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


def ble_function(ble, device_address, topics, log_level, tts_data):
    """BLE main thread.

    Args:
        ble: BLE host to scan for devices
        device_address: Target BLE device MAC address
    """

    polling_interval = 5
    device = None

    current_contact_status = ""

    config_service = None
    heartrate_service = None
    emergency_alert_service = None

    ble_state = BLEState.SCANNING
    hub_state = HubState.POLLING

    # Main loop
    while True:
        if ble_state == BLEState.SCANNING:
            devices = ble.scan(5.0)
            connected = ble.connect(device_address)
            if connected:
                ble_state = BLEState.FOUND_DEVICE

        elif ble_state == BLEState.FOUND_DEVICE:
            device = ble.connected_device

            if config_service is None:
                config_service = ConfigService(device, log_level)

            if heartrate_service is None:
                heartrate_service = HeartRateService(device, log_level)

            if emergency_alert_service is None:
                emergency_alert_service = EmergencyAlertService(device, log_level)

            # Enable notifications
            config_service.set_rssi_notifications(True, rssi_data_queue)

            heartrate_service.set_heartrate_notifications(True, heartrate_data_queue) 
            heartrate_service.set_heartrate_confidence_notifications(True, heartrate_confidence_data_queue) 
            heartrate_service.set_spO2_notifications(True, spO2_data_queue) 
            heartrate_service.set_scd_state_notifications(True, scd_data_queue) 

            emergency_alert_service.set_alert_active_notifications(True, alert_data_queue)

            # Alert AWS when new wristband is connected
            wristband_id = device_address
            message = MqttMessage(topics["wristband_connect"], {"wristband_id": wristband_id, "wristband_name": device.name})
            message_queue.put(message)
            
            text = f"{device.name}, connected."
            voice_engine_queue.put(text)
            
            # Wait for wristband to initialize after connecting
            time.sleep(2)

            ble_state = BLEState.CONNECTED

        elif ble_state == BLEState.CONNECTED:
            if hub_state == HubState.POLLING:
                # Read heart rate data periodically
                try:
                    # Wait for emergency alert notifications
                    if device.wait_for_notifications(polling_interval):
                        hub_state = HubState.READ_DATA
                        continue

                    # Check for missed emergency alert notifications
                    if emergency_alert_service.read_alert_active():
                        hub_state = HubState.READ_DATA
                        continue

                except Exception as e:
                    ble_state = BLEState.DISCONNECTED

            elif hub_state == HubState.READ_DATA:
                # Read data
                try:
                    data = {}

                    data["wristband_id"] = device_address
                    data["wristband_name"] = device.name
                    data["rssi"] = config_service.read_rssi()
                    data["heartrate"] = heartrate_service.read_heartrate()
                    data["heartrate_confidence"] = heartrate_service.read_heartrate_confidence();
                    data["spO2"] = heartrate_service.read_spO2()
                    data["spO2_confidence"] = heartrate_service.read_spO2_confidence();
                    data["contact_status"] = heartrate_service.read_scd_state()
                    data["alert_active"] = emergency_alert_service.read_alert_active()

                    # Trigger alert
                    if data["alert_active"] == 1:
                        data["alert_type"] = emergency_alert_service.read_alert_type()
                        if data["alert_type"] == "manual request" \
                            or data["alert_type"] == "fall event":
                            data["severity"] = "high"
                        else:
                            data["severity"] = "low"
                        
                        message = MqttMessage(topics["alert"], data)
                        message_queue.put(message)

                        text = f"{data['alert_type']} detected. Requesting help immediately."
                        voice_engine_queue.put(text)

                        # Set alert active to 0 after being received
                        emergency_alert_service.write_alert_active(0)

                    # Trigger warning for lost contact
                    elif data["contact_status"] == "undetected" and not current_contact_status == "undetected":
                        data["alert_active"] = 1
                        data["alert_type"] = "no_contact"
                        data["severity"] = "low"

                        if tts_data:
                            text = f"Your most recent heart rate is {data['heartrate']} BPM"
                            if data["spO2"] > 0:
                                text += f" and oxygen level is {data['spO2']} %"
                                    
                            voice_engine_queue.put(text)

                    # Update data
                    elif data["contact_status"] == "on_skin" and data["heartrate_confidence"] > 0:
                        message = MqttMessage(topics["data"], data)
                        message_queue.put(message)

                        # Check for high or low heartrate
                        if data["heartrate"] < LOW_HEARTRATE:
                            print("Low heartrate")
                            data["alert_active"] = 1
                            data["alert_type"] = "low heartrate"

                            text = f"Your heart rate is below the average resting heart rate at {data['heartrate']} BPM. Notifying staff."
                            voice_engine_queue.put(text)

                            message = MqttMessage(topics["alert"], data)
                            message_queue.put(message)
                        elif data["heartrate"] > HIGH_HEARTRATE:
                            print("High heartrate")
                            data["alert_active"] = 1
                            data["alert_type"] = "high heartrate"

                            text = f"Your heart rate is above the average resting heart rate at {data['heartrate']} BPM. Notifying staff."
                            voice_engine_queue.put(text)

                            message = MqttMessage(topics["alert"], data)
                            message_queue.put(message)


                    current_contact_status = data["contact_status"]
                    hub_state = HubState.POLLING
                        
                except Exception as e:
                    print(e)
                    ble_state = BLEState.DISCONNECTED
        
        elif ble_state == BLEState.DISCONNECTED:
            device.disconnect()

            # Alert AWS of wristband disconnect
            data = {}

            data["wristband_id"] = device_address
            data["wristband_name"] = device.name
            data["rssi"] = 0
            data["heartrate"] = 0
            data["heartrate_confidence"] = 0
            data["spO2"] = 0
            data["spO2_confidence"] = 0
            data["contact_status"] = 0
            data["alert_active"] = 1
            data["alert_type"] = "wristband disconnected"
            data["severity"] = "low"

            message = MqttMessage(topics["alert"], data)
            message_queue.put(message)

            text = f"Wristband, {device.name}, disconnected. Please power back on."
            voice_engine_queue.put(text)
            ble_state = BLEState.SCANNING


def voice_engine_function(voice_engine, enable_tts):
    """Voice Engine main thread.

    Args:
        voice_engine: VoiceEngine application wrapper
    """

    voice_engine.start()
    while voice_engine.is_running():
        try:
            text = voice_engine_queue.get()
            if enable_tts:
                voice_engine.stop()
                voice_engine.speak(text)
                voice_engine.start()
        except:
            pass


def main():
    """Main."""
    parser = argparse.ArgumentParser(description="Hub Application Software")
    parser.add_argument("--log", choices=["notset", "debug", "info", "warning", "error", "critical"], default="info", help="Set logging level")
    parser.add_argument("--tts", default=False, action="store_true", help="Enable TTS")
    parser.add_argument("--tts_data", default=False, action="store_true", help="Read heart rate and SpO2 readings using TTS")
    args = parser.parse_args()

    # Set logging level
    if args.log == "notset":
        log_level = logging.NOTSET
    elif args.log == "debug":
        log_level = logging.DEBUG
    elif args.log == "info":
        log_level = logging.INFO
    elif args.log == "warning":
        log_level = logging.WARNING
    elif args.log == "error":
        log_level = logging.ERROR
    elif args.log == "critical":
        log_level = logging.CRITICAL

    # Check for AWS IoT certificates
    if not os.path.exists(config.path_to_cert) or \
        not os.path.exists(config.path_to_key) or \
        not os.path.exists(config.path_to_root):
        print("Error: Certificate files do not exist. Please get them from AWS and edit config.py.")
        exit()

    endpoint = config.endpoint
    client_id = config.client_id
    hub_id = config.hub_mac_address
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
    client = MQTTClient(client_id, hub_id, endpoint, path_to_root, path_to_key, path_to_cert, log_level)
    client.connect()

    # Alert AWS of new Hub connection
    message_queue.put(MqttMessage(topics["hub_connect"], {"hub_name": client_id}))

    # Configure BLE host and connect to peripheral device
    ble = BLEHost(log_level)

    # Configure Voice Engine
    voice_engine = VoiceEngine(log_level)

    # Create and start threads
    mqtt_thread = threading.Thread(target=mqtt_function, args=(client, ), daemon=True)
    ble_thread = threading.Thread(target=ble_function, args=(ble, device_address, topics, log_level, args.tts_data), daemon=True)
    voice_thread = threading.Thread(target=voice_engine_function, args=(voice_engine, args.tts), daemon=True)

    mqtt_thread.start()
    ble_thread.start()
    voice_thread.start()

    # Wait until threads exit
    mqtt_thread.join()
    ble_thread.join()
    voice_thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
