import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import smbus2

def Cal_temperature(bus):
    # Read LM75 Raw Data
    LM75_Rawdata    = bus.read_word_data(LM75_address, 0)
    raw_temperature = ((LM75_Rawdata << 8) & 0xFF00) + (LM75_Rawdata >> 8) # Check Datasheet and Sample Code

    # Convert Raw to Celsius Temperature
    # Least Significant Bit is 0.5 
    Cel_temperature = (raw_temperature /128.0) * 0.5
    return Cel_temperature

def Cal_CO_ppm(ADS_out):
    Sensor_Voltage = ADS_out.voltage  
    # Sensor_Voltage = (ADS_out.value * 5) / 1023.0
    Sensor_R       = ((5 - Sensor_Voltage) / Sensor_Voltage)*10000  
    R              = (Sensor_R / 15620)
    Co_ppm        = (R**(-1.409)) * 106.13
    return Co_ppm


print("Init Sensor...")
# check U Sensor I2c address
MQ7_address  = 0x4a    
LM75_address = 0x48

# Build SMBus Class for I2c
bus = smbus2.SMBus(1)
# Build ADS1115 Class
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=MQ7_address)

while True:
    # Chose ADS1115 A0 pin for Output
    ADS_out = AnalogIn(ads, ADS.P0)
    Co_ppm = Cal_CO_ppm(ADS_out)
    Cel_temperature = Cal_temperature(bus)

    # Output CO ppm
    print("CO ppm is {:}".format(Co_ppm))   
    # Output Celsius Temperature
    print("Celsius Temperature: {:} °C".format(Cel_temperature))
    time.sleep(1)

# Close bus use I2C
bus.close()