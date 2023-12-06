

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)



def main():
    while True:
        GPIO.output(4, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(4, GPIO.LOW)
        time.sleep(1)


if __name__ == "__main__":
    main()