#!/bin/bash

# Install Python (assuming Ubuntu/Debian-based system)
if [ "$1" == '-py' ]; then
	sudo apt-get update
	sudo apt-get install python3 python3-pip -y

	# Install virtualenv
	pip3 install virtualenv
fi

config_file="/boot/config.txt"
# setup i2c spi core_freq
sudo mv "$config_file" "$config_file".bak
sudo cp './config.txt' "$config_file"

# Create a virtual environment named "ss"
virtualenv smoke_sensor 

# Activate the virtual environment
source smoke_sensor/bin/activate

pip3 install --upgrade setuptools
cd ~
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
# neopixel
pip3 install rpi_ws281x adafruit-circuitpython-neopixel
pip3 install paho-mqtt smbus2 adafruit-circuitpython-ads1x15

# Deactivate the virtual environment when done
deactivate
