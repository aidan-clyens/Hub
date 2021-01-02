# AWS IoT Device

## Getting Started
### AWS IoT
1. Create new AWS IoT Thing and generate certificates
2. Create a new AWS IoT Policy and provide permissions for topic and client ID
3. Attach policy to certificate
3. Copy certificates to *certificates* folder
4. Update *config.py* with paths to certificates

### Install Dependencies
1. Python 3 is required. Note script must be run as root.
2. Install submodules with `git submodule update --init`.
3. Install required libraries.
```
sudo apt-get install libbluetooth-dev
sudo apt-get install libboost-all-dev
```
4. Install *PyBluez*.
```
cd pybluez
sudo python3 setup.py install
```
5. Install other packages.
```
sudo pip3 install AWSIoTPythonSDK
sudo pip3 install gattlib
```

## Usage
`sudo python3 device.py`
