import paho.mqtt.client as mqtt
import json
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import smbus2
import RPi.GPIO as GPIO
import neopixel
import uuid
import threading


# LED stripe configuration
pixel_pin = board.D10
num_pixels = 60
ORDER = neopixel.GRB
PLACE="bedroom"
COLOR={
    "red":(255,0,0),
    "green":(0,255,0),
    "white":(255,255,255),
    "orange":(255,165,0),
    "none":(0,0,0)
}
show_path=False
path_pos=0
# mqtt configuration
MQTT_SERVER = "yckRPi.local"
MQTT_PORT = 1883
MQTT_ALIVE = 60
MQTT_TOPIC = [f"/{PLACE}/status","path"]
MQTT_DEVICE_NAME = "/rpi/"
# initialize
smoke_detected = False
power_detected = True
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER
)

def led_control(num):
    num=float(num/360)
    #print(num)
    pos=int(num*num_pixels)
    led_length_run=6
    led_length=2
    for i in range(30):
        pixels[i]=(COLOR["none"])
    for i in range(led_length):
        pixels[(pos+i)%30]=COLOR["green"]
        pixels[(pos-i)%30]=COLOR["green"]
    pixels.show()

    for i in range(led_length_run):
        pixels[(pos+led_length_run-i)%30]=COLOR["green"]
        pixels[(pos-led_length_run+i)%30]=COLOR["green"]
        pixels[(pos+led_length_run-i+1)%30]=COLOR["none"]
        pixels[(pos-led_length_run+i-1)%30]=COLOR["none"]
        time.sleep(0.1)
        pixels.show()
    for i in range(30):
        pixels[i]=(COLOR["none"])
    for i in range(led_length):
        pixels[(pos+i)%30]=COLOR["green"]
        pixels[(pos-i)%30]=COLOR["green"]
    pixels.show()

def led_situation(sit):
    for i in range(30):
        pixels[i+30]=COLOR[sit]
    pixels.show()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    for topic in MQTT_TOPIC:
        print(f"subscribe to {topic}")
        client.subscribe(topic)

def on_message(client, userdata, msg):
    global show_path
    global path_pos
    if (msg.topic == "path"):
        data = json.loads(msg.payload)
        path_pos=float(data[PLACE])
        led_control(float(data[PLACE]))
    elif(msg.topic ==f"/{PLACE}/status"):
        data = json.loads(msg.payload)
        led_situation(data["color"])
        if(data["color"]!="none"):
            show_path=True
        else:
            show_path=False
    #print(f"{msg.topic} - data1: {json.loads(msg.payload)['data1']}, data2: {json.loads(msg.payload)['data2']}")


def Cal_temperature(bus):
    # Read LM75 Raw Datams
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

def smoke(channel):
    global smoke_detected
    smoke_detected = not smoke_detected

def power(channel):
    global power_detected
    power_detected = not power_detected

print("Init Sensor...")
# check U Sensor I2c address
MQ7_address  = 0x4a
LM75_address = 0x48

# Build SMBus Class for I2c
bus = smbus2.SMBus(1)
# Build ADS1115 Class
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=MQ7_address)

# mqtt setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)
#mqtt_client.loop_forever()

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(13, GPIO.BOTH,callback=smoke, bouncetime=100)

GPIO.setup(18, GPIO.IN)
GPIO.add_event_detect(18, GPIO.BOTH, callback=power, bouncetime=100)

def sensor_data(channel:str,qos:int):
    global smoke_detected,power_detected
    ADS_out = AnalogIn(ads, ADS.P0)
    Co_ppm = Cal_CO_ppm(ADS_out)
    Cel_temperature = Cal_temperature(bus)
    payload = {
        'ppm': Co_ppm,
        'temp': Cel_temperature,
        'smoke': smoke_detected,
        'battery':power_detected
    }
    mqtt_client.publish(channel, json.dumps(payload), qos=qos)
    mqtt_client.loop(2,10)


def repeat_send(channel:str,qos:int,period:int):
    while True:
        sensor_data(channel,qos)
        time.sleep(period)

# send data
dataThread = threading.Thread(target = repeat_send ,args=(f"/{PLACE}/condition",1,1))
dataThread.start()

while True:
    if show_path:
        led_control(path_pos)
    if GPIO.input(18):
        led_situation("white")
    else:
        led_situation("none")
# Close bus use I2C
bus.close()