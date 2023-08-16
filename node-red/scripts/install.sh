#! /bin/bash

sudo apt update -y && sudo apt upgrade -y
# install Mosquitto
sudo apt install -y mosquitto mosquitto-clients
sudo systemctl enable mosquitto.service

# install Mysql
sudo apt install -y mariadb-server

### enter mysql
# sudo mysql -u root -p

# CREATE DATABASE sensor;
# CREATE USER 'node-red'@'localhost' IDENTIFIED BY 'node-red';
# GRANT ALL PRIVILEGES ON sensor.* TO 'node-red'@'localhost';
# FLUSH PRIVILEGES;
# use sensor;
# CREATE TABLE sensorData( Place varchar(255), Time BIGINT, Smoke Boolean, CO DOUBLE, Temperture DOUBLE );
# quit

# install node-red

bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
sudo systemctl enable nodered.service
