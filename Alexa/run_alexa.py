import os
import subprocess
import shlex
import sys

sys.path.insert(1, "4mics_hat")
from pixels import Pixels, pixels
from alexa_led_pattern import AlexaLedPattern


home_path = "/home/pi/Programs/FYDP/Alexa/alexa"
source_path = home_path + "/build/SampleApp/src"
config_path = home_path + "/build/Integration/AlexaClientSDKConfig.json"
models_path = home_path + "/third-party/alexa-rpi/models"

debug_flag = ""


pixels.pattern = AlexaLedPattern(show=pixels.show)


env = os.environ.copy()
env["PO_ALSA_PLUGHW"] = "1"

os.chdir(source_path)

cmd = f"./SampleApp {config_path} {models_path} {debug_flag}"
print(cmd)
process = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, env=env)

try:
    while True:
        output = process.stdout.readline()
        if output:
            output = output.decode().replace("\n", "").strip().lower()
            if "idle" in output:
                print("Idle")
                pixels.off()
            elif "listening" in output:
                print("Listening")
                pixels.wakeup()
            elif "thinking" in output:
                print("Thinking")
                pixels.think()
            elif "speaking" in output:
                print("Speaking")
                pixels.speak()

        exit_code = process.poll()
        if output == "" and exit_code is not None:
            break
except KeyboardInterrupt:
    pixels.off()
    exit()

