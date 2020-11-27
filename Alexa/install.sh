if ! [ -d "alexa" ]; then
    mkdir alexa
fi
cd alexa

if ! [ -f "setup.sh" ]; then
    wget https://raw.githubusercontent.com/alexa/avs-device-sdk/master/tools/Install/setup.sh 
fi

if ! [ -f "genConfig.sh" ]; then
    wget https://raw.githubusercontent.com/alexa/avs-device-sdk/master/tools/Install/genConfig.sh
fi

if ! [ -f "pi.sh" ]; then
    wget https://raw.githubusercontent.com/alexa/avs-device-sdk/master/tools/Install/pi.sh
fi

if [ -f "../config.json" ]; then
    mv ../config.json ./
fi

if [ -f "config.json" ]; then
    sudo bash setup.sh config.json
fi

sudo apt-get install gstreamer1.0-alsa gstreamer1.0-tools gstreamer1.0-plugins-ugly

cd ..
