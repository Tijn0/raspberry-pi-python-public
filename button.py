class Button:

    def __init__(self, pin, GPIO, button_debounce_time):
        self.got_pressed = False
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.on_event, bouncetime=button_debounce_time)

    def on_event(self, event):
        self.got_pressed = True

    def was_pressed(self):
        if self.got_pressed:
            self.got_pressed = False
            return True
        else:
            return False