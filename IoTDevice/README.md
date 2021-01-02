# AWS IoT Device

## Getting Started
### AWS IoT
1. Create new AWS IoT Thing and generate certificates
2. Create a new AWS IoT Policy and provide permissions for topic and client ID
3. Attach policy to certificate
3. Copy certificates to *certificates* folder
4. Update *config.py* with paths to certificates

### Install Dependencies
1. Python 3 is required. Also ensure that the user is the owner of the current directory before proceeding.
2. Install required packages with `pip install -r requirements.txt`
3. Install submodules with `git submodule update --init`
4. Install required libraries
```
sudo apt-get install libbluetooth-dev
sudo apt-get install libboost-all-dev

pip install -r requirements.txt
```
4. Install *PyBluez*
```
cd pybluez
python setup.py install
```

## Usage
`python3 device.py`
