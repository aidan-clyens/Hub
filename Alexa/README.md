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

## Resources
https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/
