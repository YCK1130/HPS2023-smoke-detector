import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BOARD)
GPIO.setup(37,GPIO.IN)   
 
try:
    while True:
        if GPIO.input(37):    
            print("有偵測到問題")
            break
        else:
            print("沒有偵測到問題")
except  KeyboardInterrupt:
    print("Stop")
    GPIO.cleanup()
