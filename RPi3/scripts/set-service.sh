#!/usr/bin/env sh

WORKSPACE="/home/pi/HPS2023-smoke-detector"

cd $WORKSPACE/RPi3/system
sudo cp sensor.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable sensor.service
sudo systemctl start sensor.service