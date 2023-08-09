import smbus2
import time

def Cal_temperature(bus):
    # Read LM75 Raw Data
    LM75_Rawdata    = bus.read_word_data(LM75_address, 0)
    raw_temperature = ((LM75_Rawdata << 8) & 0xFF00) + (LM75_Rawdata >> 8) # Check Datasheet and Sample Code

    # Convert Raw to Celsius Temperature
    # Least Significant Bit is 0.5 
    Cel_temperature = (raw_temperature / 32.0) * 0.125
    return Cel_temperature

bus_number = 1

# check U LM75 I2C address
LM75_address = 0x48

# Build SMBus Class for I2c
bus = smbus2.SMBus(1)

while True:

    Cel_temperature = Cal_temperature(bus)
    # Output Celsius Temperature
    print("Celsius Temperature: {:} °C".format(Cel_temperature))
    time.sleep(1)

# Close bus use I2C
bus.close()