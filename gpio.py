import RPi.GPIO as GPIO
from time import sleep
from config import indexes

# setting up GPIO counting standard as BCM
GPIO.setmode(GPIO.BCM)

# setting up GPIOs as Inputs
GPIO.setup(indexes['door_1'], GPIO.IN)
GPIO.setup(indexes['door_2'], GPIO.IN)
GPIO.setup(indexes['screen'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(indexes['button'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(indexes['led_1'], GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(indexes['led_2'], GPIO.OUT, initial=GPIO.HIGH)


# storing results
def update_input():
    door_1_status = GPIO.input(indexes['door_1'])
    door_2_status = GPIO.input(indexes['door_2'])
    screen_status = GPIO.input(indexes['screen'])
    button_status = GPIO.input(indexes['button'])
    print("BUTTON =", button_status)
    return door_1_status, door_2_status, screen_status, button_status




def change_output(state):
    if state:
        led_1 = GPIO.output(indexes['led_1'], GPIO.LOW)
        led_2 = GPIO.output(indexes['led_2'], GPIO.LOW)
        state_1 = GPIO.gpio_function(indexes['led_1'])
        state_2 = GPIO.gpio_function(indexes['led_2'])
        print("LED 1 :", led_1, state_1)
        print("LED 2 :", led_2, state_2)
    else:
        while not state:
            led_1 = GPIO.output(indexes['led_1'], GPIO.HIGH)
            led_2 = GPIO.output(indexes['led_2'], GPIO.HIGH)
            state_1 = GPIO.gpio_function(indexes['led_1'])
            state_2 = GPIO.gpio_function(indexes['led_2'])
            print("LED 1 :", led_1, state_1)
            print("LED 2 :", led_2, state_2)
            sleep(1)
            led_1 = GPIO.output(indexes['led_1'], GPIO.LOW)
            led_2 = GPIO.output(indexes['led_2'], GPIO.LOW)
            sleep(1)

while (1):
    print(update_input())
    sleep(1)