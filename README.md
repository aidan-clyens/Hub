# FYDP Hub

## Getting Started
1. Setup AWS IoT and Alexa Voice Service module
[AWS IoT Setup](IoTDevice/README.md)
[Alexa Voice Service Setup](Alexa/README.md)

2. Add the following lines to *~/.bashrc*
```
sleep 10
screen /home/pi/Programs/FYDP/IoTDevice/start.sh
screen python3 /home/pi/Programs/FYDP/Alexa/run_alexa.py
```
Replace the project directory as necessary
