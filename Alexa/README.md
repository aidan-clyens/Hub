# Amazon Alexa

## Getting Started
### Seeed Voice Card
1. Install Seeed voice card driver
```
sudo apt-get update
sudo apt-get upgrade
git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard
sudo ./install.sh  
reboot
```
2. Select Raspberry Pi audio output in `raspi_config`
3. Check sound card with `arecord -L`

### APA102 LEDs
1. Enable SPI in `raspi-config`
2. Install APA102 LEDs library
```
git clone https://github.com/respeaker/4mics_hat.git
pip install spidev gpiozero
```
### Alexa Voice Service
1. Sign into an Amazon Developer account
2. Go to Alexa Voice Service -> Products -> Add New Product
3. Create new product and Security Profile, make sure to download config file
4. Copy *config.json* file to this directory
5. Run `./install.sh`


## Resources
https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/
https://www.ionos.com/digitalguide/server/configuration/raspberry-pi-alexa/
