# FYDP Hub

## Getting Started
1. Setup AWS IoT and Alexa Voice Service module
[AWS IoT Setup](IoTDevice/README.md)
[Alexa Voice Service Setup](Alexa/README.md)

2. Add the following lines to *~/.bashrc*
```
sleep 10
screen -d -m /home/pi/Programs/FYDP/IoTDevice/start.sh
screen -d -m /home/pi/Programs/FYDP/Alexa/run_alexa.sh
```
Replace the project directory as necessary
