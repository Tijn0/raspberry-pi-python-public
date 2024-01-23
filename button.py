import time
import logging

class Button:

    def __init__(self, pin, GPIO, button_debounce_time):
        self.got_pressed = False
        self.got_long_pressed = False
        self.pin = pin
        self.GPIO = GPIO
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.on_event, bouncetime=button_debounce_time)

    def on_event(self, event) -> None:
        button_state = self.GPIO.input(self.pin)
        held_down_time = 0
        while not self.GPIO.input(self.pin):
            held_down_time += 1
            print(held_down_time)
            time.sleep(0.02)
            if held_down_time > 50:
                logging.info(f"Button at pin {self.pin} got long pressed")
                self.got_long_pressed = True
                break
        if held_down_time > 50:
            return
        logging.info(f"Button at pin {self.pin} got pressed")
        self.got_pressed = True

    def was_pressed(self) -> bool:
        if self.got_pressed:
            self.got_pressed = False
            return True
        else:
            return False

    def was_held_down(self) -> bool:
        if self.got_long_pressed:
            self.got_long_pressed = False
            return True
        else:
            return False