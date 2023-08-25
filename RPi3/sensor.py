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
PLACE = "bedroom"
COLOR = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "white": (255, 255, 255),
    "orange": (255, 165, 0),
    "none": (0, 0, 0)
}
stateColor = {
    "normal": "none",
    "abnormal": "orange",
    "battery": "white",
    "fire": "red"
}
# state machine
STATUS = "normal"
statusMachine = {
    "status": {
        "state": STATUS,
        "color": "none",
        "time": time.time()
    },
    "transition": {
        "normal": {
            "green": "normal",
            "orange": "abnormal",
            "red": "fire",
            "battery": "battery",
            "power": "normal",
            "reset": "normal"
        },
        "abnormal": {
            "green": "normal",
            "orange": "abnormal",
            "red": "fire",
            "battery": "abnormal",
            "power": "abnormal",
            "reset": "normal"
        },
        "fire": {
            "green": "normal",
            "orange": "fire",
            "red": "fire",
            "battery": "fire",
            "power": "fire",
            "reset": "normal"
        },
        "battery": {
            "green": "normal",
            "orange": "abnormal",
            "red": "fire",
            "battery": "battery",
            "power": "normal",
            "reset": "normal"
        },
    }
}

pathMachine = {
    "status": {
        "state": "hide",
        "path_pos": 0,
        "time": time.time(),
        "use_time": time.time()
    },
    "transition": {
        "hide": {
            "NORMAL": "hide",
            "FIRE": "show",
            "reset": "hide"
        },
        "show": {
            "NORMAL": "show",
            "FIRE": "show",
            "reset": "hide"
        },
    }
}


def transition(stateMachine, action):
    current_status = stateMachine["status"]["state"]
    try:
        next = stateMachine["transition"][current_status][action]
        stateMachine["status"]["state"] = next
        stateMachine["status"]["time"] = time.time()
        print(f"switch to state: {next} by {action}")
    except Exception:
        print(f"FAIL to switch state, {current_status}:{action} not defined!")
        pass


# mqtt configuration
MQTT_SERVER = "yckRPi.local"
MQTT_PORT = 1883
MQTT_ALIVE = 60
MQTT_TOPIC = [f"/{PLACE}/status", "path"]
MQTT_DEVICE_NAME = "/rpi/"
# initialize
smoke_detected = False
power_detected = True
DURATION = 1
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.5, auto_write=False, pixel_order=ORDER
)


def led_control(num):
    num = float(num/360)
    # print(num)
    pos = int(num*num_pixels)
    led_length_run = 6
    led_length = 2
    for i in range(30):
        pixels[i] = (COLOR["none"])
    if num < 0:
        pixels.show()
        return
    for i in range(led_length):
        pixels[(pos+i) % 30] = COLOR["green"]
        pixels[(pos-i) % 30] = COLOR["green"]
    pixels.show()

    for i in range(led_length_run):
        pixels[(pos+led_length_run-i) % 30] = COLOR["green"]
        pixels[(pos-led_length_run+i) % 30] = COLOR["green"]
        pixels[(pos+led_length_run-i+1) % 30] = COLOR["none"]
        pixels[(pos-led_length_run+i-1) % 30] = COLOR["none"]
        time.sleep(0.1)
        pixels.show()
    for i in range(30):
        pixels[i] = (COLOR["none"])
    for i in range(led_length):
        pixels[(pos+i) % 30] = COLOR["green"]
        pixels[(pos-i) % 30] = COLOR["green"]
    pixels.show()


def led_situation(sit):
    for i in range(30):
        pixels[i+30] = COLOR[sit]


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    for topic in MQTT_TOPIC:
        print(f"subscribe to {topic}")
        client.subscribe(topic)


def on_message(client, userdata, msg):
    global statusMachine, pathMachine
    if (msg.topic == "path"):
        data = json.loads(msg.payload)
        path_pos = float(data[PLACE])
        # print(data)
        transition(pathMachine, data["trigger"])
        pathMachine["status"]["path_pos"] = path_pos
    elif (msg.topic == f"/{PLACE}/status"):
        data = json.loads(msg.payload)
        transition(statusMachine, data["color"])
        statusMachine["status"]["color"] = data["color"]
        # led_situation(data["color"])
        # if (data["color"] != "none"):
        #     show_path = True
        # else:
        #     show_path = False
    # print(f"{msg.topic} - data1: {json.loads(msg.payload)['data1']}, data2: {json.loads(msg.payload)['data2']}")


def Cal_temperature(bus):
    # Read LM75 Raw Datams
    LM75_Rawdata = bus.read_word_data(LM75_address, 0)
    raw_temperature = ((LM75_Rawdata << 8) & 0xFF00) + \
        (LM75_Rawdata >> 8)  # Check Datasheet and Sample Code

    # Convert Raw to Celsius Temperature
    # Least Significant Bit is 0.5
    Cel_temperature = (raw_temperature / 128.0) * 0.5
    return Cel_temperature


def Cal_CO_ppm(ADS_out):
    Sensor_Voltage = ADS_out.voltage
    # Sensor_Voltage = (ADS_out.value * 5) / 1023.0
    Sensor_R = ((5 - Sensor_Voltage) / Sensor_Voltage)*10000
    R = (Sensor_R / 15620)
    Co_ppm = (R**(-1.409)) * 106.13
    return Co_ppm


def smoke(channel):
    global smoke_detected, smoke_time
    if (time.time()-smoke_time > DURATION):
        smoke_detected = not smoke_detected


def power(channel):
    # true : battery
    global power_detected, statusMachine
    # GPIO input high => battery
    time.sleep(0.1)
    power_detected = GPIO.input(channel)
    action = "power"
    if power_detected:
        action = "battery"
    transition(statusMachine, action)


def setLED():
    global statusMachine, pathMachine
    statusState = statusMachine["status"]["state"]
    statusTime = statusMachine["status"]["time"]
    pathState = pathMachine["status"]["state"]
    pathTime = pathMachine["status"]["time"]
    usePathTime = pathMachine["status"]["use_time"]

    nowTime = time.time()
    if nowTime - statusTime < 2:
        print(statusMachine["status"]["color"])
        led_situation(stateColor[statusMachine["status"]["state"]])
    if nowTime - usePathTime > 1:
        if pathState == "show":
            led_control(pathMachine["status"]["path_pos"])
            if statusState == "normal" or statusState == "battery":
                led_situation("green")
        if pathState == "hide":
            led_control(-1)
            print(statusState)
            if statusState == "normal":
                led_situation("none")
    pixels.show()


def LED_daemon():
    while True:
        setLED()
        time.sleep(0.5)


print("Init Sensor...")
# check U Sensor I2c address
MQ7_address = 0x4a
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
# mqtt_client.loop_forever()

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(13, GPIO.BOTH, callback=smoke, bouncetime=100)

GPIO.setup(18, GPIO.IN)
GPIO.add_event_detect(18, GPIO.BOTH, callback=power, bouncetime=100)


def sensor_data(channel: str, qos: int):
    global smoke_detected, power_detected
    try:
        ADS_out = AnalogIn(ads, ADS.P0)
        Co_ppm = Cal_CO_ppm(ADS_out)
    except Exception:
        Co_ppm = 0.7

    try:
        Cel_temperature = Cal_temperature(bus)
    except Exception:
        Cel_temperature = 25.625
    payload = {
        'ppm': Co_ppm,
        'temp': Cel_temperature,
        'smoke': int(smoke_detected),
        'battery': power_detected
    }
    mqtt_client.publish(channel, json.dumps(payload), qos=qos)
    mqtt_client.loop(2, 10)


def repeat_send(channel: str, qos: int, period: int):
    while True:
        sensor_data(channel, qos)
        time.sleep(period)


# send data
dataThread = threading.Thread(
    target=repeat_send, args=(f"/{PLACE}/condition", 1, 1))
dataThread.start()

LEDThread = threading.Thread(target=LED_daemon)
LEDThread.start()

smoke_time = time.time()


# while True:
#     if show_path:
#         led_control(path_pos)
#     if GPIO.input(18):
#         led_situation("white")
#     else:
#         led_situation("none")
# # Close bus use I2C
dataThread.join()
LEDThread.join()

bus.close()
