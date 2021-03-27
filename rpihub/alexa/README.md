# Amazon Alexa
## Getting Started
### Install Dependencies
1. Install submodules `git submodule update --init`
2. Install Seeed voice card driver
```
cd rpi-hub/alexa/seeed-voicecard
sudo ./install.sh  
sudo reboot
```
3. Select Raspberry Pi audio output in `raspi_config`
4. Check sound card with `arecord -L`
5. Enable SPI in `raspi-config` for APA102 LEDs package
6. Install dependencies for APA102 LEDs library
```
pip3 install spidev gpiozero
```
7. Install mplayer for Text-to-Speech
```
sudo apt-get install mplayer
```

### Alexa Voice Service
1. Sign into an Amazon Developer account
2. Go to Alexa Voice Service -> Products -> Add New Product
3. Create new product and Security Profile, make sure to download config file
4. Copy *config.json* file to this directory
5. Run `./install.sh`
6. Run the AVS SDK SampleApp for the first time and authorize using the code provided

### AWS CLI
1. Install AWS CLI version 1
```
pip3 install awscli
```
2. Configure AWS CLI
```
aws configure
```

## Running
`python3 run_alexa.py`


## Resources
https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/
https://www.ionos.com/digitalguide/server/configuration/raspberry-pi-alexa/
