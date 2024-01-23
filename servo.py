import logging
import time


class Servo:
    def __init__(self, servo_pin, GPIO):
        GPIO.setup(servo_pin, GPIO.OUT)
        self.GPIO = GPIO
        self.servo_pin = servo_pin
        self.pwm = GPIO.PWM(servo_pin, 50)
        self.pwm.start(0)
        self.locked = False

        self.unlock()
        time.sleep(1)

    def lock(self):
        if not self.locked:
            self.GPIO.output(self.servo_pin, self.GPIO.HIGH)
            self.pwm.ChangeDutyCycle(7.2)
            time.sleep(1)
            self.GPIO.output(self.servo_pin, self.GPIO.LOW)
            self.pwm.ChangeDutyCycle(0)

            self.locked = True
        else:
            logging.warning("SAFE IS ALREADY LOCKED")

    def unlock(self):
        if self.locked:
            self.GPIO.output(self.servo_pin, self.GPIO.HIGH)
            self.pwm.ChangeDutyCycle(21.6)
            time.sleep(1)
            self.GPIO.output(self.servo_pin, self.GPIO.LOW)
            self.pwm.ChangeDutyCycle(0)

            self.locked = False
        else:
            logging.warning("SAFE IS ALREADY UNLOCKED")
