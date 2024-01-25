import time
import logging


class RotaryEncoder:
    def __init__(self, encoder_s1_pin, encoder_s2_pin, GPIO, rotary_encoder_debounce_time):
        GPIO.setup(encoder_s1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(encoder_s2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(encoder_s1_pin, GPIO.FALLING, callback=self.on_event, bouncetime=rotary_encoder_debounce_time)
        self.encoder_s1_pin = encoder_s1_pin
        self.encoder_s2_pin = encoder_s2_pin
        self.GPIO = GPIO
        self.selected_number = 0
        self.selected_number_before_direction_changed = 0
        self.current_direction = False
        self.last_direction = False
        self.last_selected_number = 0
        self.distance_travelled_on_direction = 0
        self.direction_changed_input = False
        self.number_changed_input = False

    def on_event(self, event) -> None:
        time.sleep(0.004)

        switch_a = self.GPIO.input(self.encoder_s1_pin)
        switch_b = self.GPIO.input(self.encoder_s2_pin)
        logging.debug("ROTARY ENCODER event detected!")
        if switch_a == 0 and switch_b == 1:  # Rotary encoder turned to the left
            self.update_selected_number(False)
            self.update_direction(False)

        else:  # Rotary encoder turned to the right
            self.update_selected_number(True)
            self.update_direction(True)

    def update_selected_number(self, direction: bool) -> None:
        self.last_selected_number = self.selected_number
        if direction:  # Rotary encoder turned to the right
            if self.selected_number < 19:
                self.selected_number += 1
            else:
                self.selected_number = 0

        else:  # Rotary encoder turned to the left
            if self.selected_number > 0:
                self.selected_number -= 1
            else:
                self.selected_number = 19
        self.number_changed_input = True
        logging.debug(f"UPDATED selected nummer ({self.last_selected_number} -> {self.selected_number})")

    def update_direction(self, direction: bool) -> None:
        self.last_direction = self.current_direction
        self.current_direction = direction

        if self.direction_changed():

            if direction:
                direction_debug_string = "LEFT -> RIGHT"
            else:
                direction_debug_string = "RIGHT -> LEFT"

            logging.debug(f"ROTARY ENCODER DIRECTION {direction_debug_string}")
            self.direction_changed_input = True
            self.distance_travelled_on_direction = 0
        else:
            self.distance_travelled_on_direction += 1

    def direction_changed(self) -> bool:
        if self.last_direction != self.current_direction:
            self.selected_number_before_direction_changed = self.last_selected_number
            logging.debug("Direction changed")
            return True  # Direction changed
        else:
            return False  # Direction didn't change

    def direction_changed_event(self) -> bool:
        if self.direction_changed_input:
            self.direction_changed_input = False
            return True
        else:
            return False

    def number_changed_event(self) -> bool:
        if self.number_changed_input:
            self.number_changed_input = False
            return True
        else:
            return False

    def reset_direction(self) -> None:
        self.current_direction = False
        self.last_direction = False
        self.direction_changed_input = False
        self.number_changed_input = False
        self.distance_travelled_on_direction = 0

