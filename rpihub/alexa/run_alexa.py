import os
import signal
import subprocess
import shlex
import sys
import logging
import threading
import queue
import time

package_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(package_dir, "4mics_hat"))
from pixels import Pixels, pixels
from alexa_led_pattern import AlexaLedPattern

from rpihub.logger import get_logger


sample_script = os.path.join(package_dir, "run_alexa.sh")
tts_script = os.path.join(package_dir, "speech.sh")


class VoiceEngine:
    def __init__(self, log_level):
        # Configure logger
        self.logger = get_logger(__name__, log_level)

        # Configure LEDs
        self.pixels = pixels
        self.pixels.pattern = AlexaLedPattern(show=self.pixels.show)

        self.env = os.environ.copy()
        self.env["PA_ALSA_PLUGHW"] = "1"

        self.started = False

    def __del__(self):
        self.pixels.off()

    def start(self):
        self.logger.info("Starting AVS")
        cmd = f"bash {sample_script}"
        self.logger.debug(cmd)
        self.process = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, env=self.env)
        self.started = True

        self.process_queue = queue.Queue()
    
        self.output_thread = threading.Thread(target=self.read_output, args=(self.process.stdout, self.process_queue, self.started))
        self.output_thread.daemon = True
        self.output_thread.start()

    def is_running(self):
        exit_code = self.process.poll()
        if exit_code is not None:
            self.started = False

        return self.started

    def stop(self):
        if not self.started:
            return

        self.logger.info("Stopping AVS")

        cmd = "ps -a"
        ps_process = subprocess.Popen(shlex.split(cmd), shell=False, stdout=subprocess.PIPE)
        out, err = ps_process.communicate()

        for line in out.splitlines():
            if "SampleApp" in str(line):
                pid = int(line.split(None, 1)[0])
                os.kill(pid, signal.SIGKILL)

        while self.is_running():
            pass

    def read_output(self, pipe, process_queue, running):
        while running:
            output = pipe.readline()

            if output:
                output = output.decode().replace("\n", "").strip().lower()
                if "to authorize" in output:
                    code = output[output.find("code:")+5:].upper()
                    self.logger.warning(f"Authorize at https://amazon.com/us/code with code: {code}")
                if "idle" in output:
                    self.idle()
                elif "listening" in output:
                    self.listening()
                elif "thinking" in output:
                    self.thinking()
                elif "speaking" in output:
                    self.speaking()

        self.logger.debug("AVS output thread stopped")

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

    def speak(self, text):
        cmd = f"bash {tts_script} {text}"
        self.logger.debug(cmd)
        self.pixels.speak()
        subprocess.run(shlex.split(cmd), shell=False, stdout=subprocess.PIPE, env=self.env)
        self.pixels.off()


def main():
    prev_time = time.time() * 1000

    alexa = VoiceEngine()
    alexa.start()
    while alexa.is_running():
        curr_time = time.time() * 1000
        if curr_time - prev_time > 10000:
            alexa.stop()
            alexa.speak("Wristband, Aidan Wristband, connected")
            alexa.start()

            prev_time = curr_time


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()

