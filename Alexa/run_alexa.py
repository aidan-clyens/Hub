import os
import subprocess
import shlex
import sys
import logging

sys.path.insert(1, "4mics_hat")
from pixels import Pixels, pixels
from alexa_led_pattern import AlexaLedPattern


source_path = os.path.join(os.getcwd(), "alexa/build/SampleApp/src")
config_path = os.path.join(os.getcwd(), "alexa/build/Integration/AlexaClientSDKConfig.json")
models_path = os.path.join(os.getcwd(), "alexa/third-party/alexa-rpi/models")

sample_app = os.path.join(source_path, "SampleApp")

debug_flag = ""


class Alexa:
    def __init__(self):
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        streamHandler.setFormatter(formatter)
        self.logger.addHandler(streamHandler)

        # Configure LEDs
        self.pixels = pixels
        self.pixels.pattern = AlexaLedPattern(show=pixels.show)

        self.env = os.environ.copy()
        self.env["PO_ALSA_PLUGHW"] = "1"

        self.started = False

    def __del__(self):
        self.pixels.off()

    def start(self):
        cmd = f"{sample_app} {config_path} {models_path} {debug_flag}"
        self.logger.debug(cmd)
        process = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, env=self.env)

        self.started = True

        while True:
            output = process.stdout.readline()
            if output:
                output = output.decode().replace("\n", "").strip().lower()
                if "idle" in output:
                    self.idle()
                elif "listening" in output:
                    self.listening()
                elif "thinking" in output:
                    self.thinking()
                elif "speaking" in output:
                    self.speaking()

            exit_code = process.poll()
            if output == "" and exit_code is not None:
                break

    def idle(self):
        self.logger.info("Idle")
        self.pixels.off()

    def listening(self):
        self.logger.info("Listening")
        self.pixels.wakeup()

    def thinking(self):
        self.logger.info("Thinking")
        self.pixels.think()

    def speaking(self):
        self.logger.info("Speaking")
        self.pixels.speak()


def main():
    alexa = Alexa()
    alexa.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()

