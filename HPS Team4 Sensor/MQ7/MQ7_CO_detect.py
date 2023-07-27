import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def Cal_CO_ppm(ADS_in):
    Sensor_Voltage = ADS_in.voltage  
    # Sensor_Voltage = (ADS_in.value * 5) / 1023.0
    Sensor_R       = ((5 - Sensor_Voltage) / Sensor_Voltage)*10000  
    R              = (Sensor_R / 15620)
    Co_ppm        = (R**(-1.409)) * 106.13
    return Co_ppm

MQ7_address = 0x4a

# Build ADS1115 Class
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=MQ7_address)

while True:
    # Chose ADS1115 A0 pin for Output
    ADS_in = AnalogIn(ads, ADS.P0)
    Co_ppm = Cal_CO_ppm(ADS_in)
    print("CO ppm is {:.}".format(Co_ppm))   
    time.sleep(1)