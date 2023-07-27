2023/06 ~ 2023/09

## LM75

LM75 <br>
<img src="https://i.imgur.com/NpOCn10.jpg" width="300px"> <br>
We use LM75 to monitor Celsius temperature.


Python Module Requirements   <br>
```
sudo pip install smbus2
```


[LM75 DataSheet](https://www.analog.com/media/en/technical-documentation/data-sheets/LM75.pdf)、[LM75 Sample code](https://github.com/leon-anavi/rpi-examples/tree/master)

---

## MQ7
MQ7 <br>
<img src="https://i.imgur.com/oTL3SgU.jpg" width="300px"> <br>
ADS1115 <br>
<img src="https://i.imgur.com/YcCYMgB.jpg" width="300px">

<br>

We use MQ7 to detect the concentration of CO (carbon monoxide) in the air, measured in ppm (parts per million). Since RPI lacks an Analog-to-Digital Converter (ADC) to read the output voltage from the MQ7 Ao pin, we have additionally connected an ADS1115 ADC.

Python Module Requirements

```
sudo pip install adafruit-circuitpython-ads1x15
```


The MQ7 carbon monoxide sensor requires preheating (powering up) for approximately 3 to 5 minutes before its measured values become relatively stable.

[MQ7 Concepts](http://www.arduinohobby.euweb.cz/toppage7.htm)、[MQ7 Datasheet](https://www.sparkfun.com/datasheets/Sensors/Biometric/MQ-7.pdf)、[ADS1115 Python Module Document](https://docs.circuitpython.org/projects/ads1x15/en/latest/api.html#analog-in)、[ADS1115 DataSheet](https://www.ti.com/lit/ds/symlink/ads1114.pdf)

---

## Smoke Detecto

<img src="https://i.imgur.com/7JkleiQ.jpg" width="300px">

For the smoke detector, we use the YDS-H03 smoke sensor. Using an oscilloscope, we identify the appropriate pins that can be connected, and then send the sensor data to the Raspberry Pi (RPI). This setup serves as a basis for detecting fire incidents.

Python Module Requirements   <br>
```
pip install RPi.GPIO
```


## Hardware Connections Pin

MQ7 Vcc  <-> LM75 Vcc <-> ADS1115 Vcc <-> RPI 5V <br>
MQ7 GND  <-> LM75 GND <-> ADS1115 GND <-> RPI GND <br>
LM75 SDA <-> ADS1115 SDA <-> ADS1115 ADDR <-> RPI SDA <br>
LM75 SCL <-> ADS1115 SCL <-> RPI SCL <br>
MQ7 Ao  <-> ADS1115 A0 <br>

---

## Program


In the folder, there are separate programs for each sensor. Additionally, there is a file named `combine_sensor.py` that integrates the Python files for both sensors. The `test_alarm.py` program is used purely to test whether the GPIO signal from the smoke detector can be successfully read by the Raspberry Pi (RPI).

And [ChatGPT](https://chat.openai.com/auth/login?next=%2F) is you GoodFriend to help you build program.
