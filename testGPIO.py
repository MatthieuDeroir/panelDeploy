import RPi.GPIO as GPIO
from time import sleep

# setting up GPIO counting standard as BCM
GPIO.setmode(GPIO.BCM)

# GPIO's indexes
door_1_index = 2
door_2_index = 3
power_index = 22
led_1_index = 17
led_2_index = 27

# setting up GPIOs as Inputs
GPIO.setup(door_1_index, GPIO.IN)
GPIO.setup(door_2_index, GPIO.IN)
GPIO.setup(power_index, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_1_index, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(led_2_index, GPIO.OUT, initial=GPIO.HIGH)

while (1):
    print(GPIO.input(door_1_index))
    print(GPIO.input(door_2_index))
    print(GPIO.input(power_index))
