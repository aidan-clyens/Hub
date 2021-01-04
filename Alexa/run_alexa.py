import os
import subprocess
import shlex
import sys

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
        self.pixels = pixels
        self.pixels.pattern = AlexaLedPattern(show=pixels.show)

        self.env = os.environ.copy()
        self.env["PO_ALSA_PLUGHW"] = "1"

    def __del__(self):
        self.pixels.off()

    def start(self):
        cmd = f"{sample_app} {config_path} {models_path} {debug_flag}"
        print(cmd)
        process = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, env=self.env)

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
        print("Idle")
        self.pixels.off()

    def listening(self):
        print("Listening")
        self.pixels.wakeup()

    def thinking(self):
        print("Thinking")
        self.pixels.think()

    def speaking(self):
        print("Speaking")
        self.pixels.speak()


def main():
    alexa = Alexa()
    alexa.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()

