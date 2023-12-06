

import RPi.GPIO as GPIO
import time
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
print("starting")


def main():
    while True:
        GPIO.output(4, GPIO.HIGH)
        time.sleep(0.0003)
        GPIO.output(4, GPIO.LOW)
        time.sleep(0.0003)


if __name__ == "__main__":
    main()