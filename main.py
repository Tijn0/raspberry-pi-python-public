# SafeSafe: Secure Storage Solutions

import RPi.GPIO as GPIO
import random
import I2C_LCD_driver
import time
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
# pins configuration
enc_a = 26  # s1
enc_b = 19  # s2
buzzer_pin = 5  # connected to buzzer +
submit_button_pin = 21

# debounce stuff
button_debounce_time = 100

# puzzle settings
safe_code_length = 3

# Sound settings
access_granted_frequency = 1000  # Hz
access_granted_duration = 200    # milliseconds

access_denied_frequency = 400    # Hz
access_denied_duration = 300     # milliseconds

custom_lcd_characters =[
[  # left arrow
    0b00000,
    0b00100,
    0b01100,
    0b11111,
    0b11111,
    0b01100,
    0b00100,
    0b00000
],
[  # right arrow
	0b00000,
	0b00100,
	0b00110,
	0b11111,
	0b11111,
	0b00110,
	0b00100,
	0b00000
]]


class DisplayGraphics:

    def __init__(self, display):
        self.display = display

    def display_progress_bar(self, duration: int, row: int=2, column: int=0, clear_display_first: bool=False):
        """
        Displays a progress bar that'll fill up within a given time
        :param duration: duration in seconds
        :param row: numbered 1-2 (1: top row)
        :param column: numbered 0-15 (0: first column)
        :param clear_display_first: clears the display of content before displaying the progress bar
        :return:
        """
        period = duration / 14

        if clear_display_first:
            self.display.clear_display()

        for amount in range(1, 15):
            bar = f"[{'='*amount}{(14-amount)*' '}]"
            self.display.display_string(bar, row=row, column=column, clear_display_first=clear_display_first)
            time.sleep(period)

    def display_code_progress(self, user_code_length: int=0, direction: bool= False, row: int=2, column: int=0, clear_display_first: bool=False) -> None:
        """
        Prints a little graphic on the LCD that lets you see your progress on the code
        :param user_code_length: how much of the code is already selected
        :param direction: the direction (dial) in which the next number will be selected (True: right, False: left)
        :param row: numbered 1-2 (1: top row)
        :param column: numbered 0-15 (0: first column)
        :param clear_display_first: clears the display of content before displaying the progress indicator
        :return:
        """
        progress_indicator = f"Code: [{user_code_length * '*'}{(safe_code_length - user_code_length) * '_'}]"
        self.display.display_string(progress_indicator, row=row, column=column, clear_display_first=clear_display_first)
        if direction:  # Right
            self.display.display_right_arrow()
        else: # Left
            self.display.display_left_arrow()



class Display:
    def __init__(self):
        self.lcd = I2C_LCD_driver.lcd()
        self.lcd.lcd_load_custom_chars(custom_lcd_characters)


    def display_string(self, string: str, row: int=1, column: int=0, clear_display_first: bool=True) -> None:
        """
        Displays a string on the display
        :param string: the string to display
        :param row: numbered 1-2 (1: top row)
        :param column: numbered 0-15 (0: first column)
        :param clear_display_first: clears the display of content before displaying the string
        :return:
        """
        if clear_display_first:
            self.clear_display()

        self.lcd.lcd_display_string(string, row, column)

    def display_left_arrow(self):
        self.lcd.lcd_write_char(0)

    def display_right_arrow(self):
        self.lcd.lcd_write_char(1)

    def clear_display(self):
        """
        clears the display
        :return:
        """
        self.lcd.lcd_clear()


class RotaryEncoder:
    def __init__(self):
        GPIO.setup(enc_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(enc_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(enc_a, GPIO.FALLING, callback=self.on_event, bouncetime=2)
        self.selected_number = 0
        self.selected_number_before_direction_changed = 0
        self.current_direction = False
        self.last_direction = False
        self.last_selected_number = 0
        self.distance_travelled_on_direction = 0
        self.direction_changed_input = False

    def on_event(self, event):
        time.sleep(0.004)

        switch_a = GPIO.input(enc_a)
        switch_b = GPIO.input(enc_b)

        if switch_a == 0 and switch_b == 1:  # Rotary encoder turned to the left
            self.update_selected_number(False)
            self.update_direction(False)

        else:  # Rotary encoder turned to the right
            self.update_selected_number(True)
            self.update_direction(True)

    def update_selected_number(self, direction: bool):
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

    def update_direction(self, direction: bool):
        self.last_direction = self.current_direction
        self.current_direction = direction

        if self.direction_changed():
            self.direction_changed_input = True
            self.distance_travelled_on_direction = 0
        else:
            self.distance_travelled_on_direction += 1

    def direction_changed(self) -> bool:
        if self.last_direction != self.current_direction:
            self.selected_number_before_direction_changed = self.last_selected_number
            return True  # Direction changed
        else:
            return False  # Direction didn't change

    def direction_changed_event(self) -> bool:
        if self.direction_changed_input:
            self.direction_changed_input = False
            return True
        else:
            return False

class SafeSafeFirmware:
    def __init__(self):
        self.buzzer = Buzzer()
        self.safe_code = SafeCode()
        self.user_code_handler = UserCode()
        self.display = Display()
        self.rotary_encoder = RotaryEncoder()

    def startup_animation(self):

        message = "Starting SafeSafe!"
        dots = []
        for i in range(0, 3):
            [dots.append(i) for i in range(1, 4)]
        self.display.display_string(f"SafeSafe OS", clear_display_first=True)
        self.display.display_string(f"Booting", clear_display_first=False, row=2)
        for amount in dots:
            self.display.display_string(('.' * amount)+(3-amount)*" ", row=2, column=7, clear_display_first=False)
            time.sleep(1)
        self.display.clear_display()
        self.buzzer.play_jingle()

    def access_granted(self):
        self.display.display_string("ACCESS GRANTED")
        self.buzzer.access_granted_tone()
        self.safe_code.return_to_first_digit()

    def access_denied(self):
        self.display.display_string("ACCESS DENIED")
        self.buzzer.access_denied_tone()
        self.safe_code.return_to_first_digit()


class SafeSafeCrackFirmware:
    def __init__(self):
        self.buzzer = Buzzer()
        self.safe_code = SafeCode()
        self.user_code_handler = UserCode()
        self.display = Display()
        self.rotary_encoder = RotaryEncoder()

    def startup_animation(self):
        message = "Starting SafeSafe!"
        dots = []
        self.display.display_string(f">Injecting Crack", clear_display_first=True)
        display_graphics = DisplayGraphics(self.display)
        display_graphics.display_progress_bar(5)
        self.display.display_string("SafeSafeCrack")
        # for amount in dots:
        # display.display_string(('.' * amount)+(3-amount)*" ", row=2, column=8, clear_display_first=False)
        # time.sleep(1)
        self.buzzer.play_jingle()

    def access_granted(self):
        self.display.display_string("ACCESS GRANTED")
        self.buzzer.access_granted_tone()
        self.safe_code.return_to_first_digit()


    def access_denied(self):
        self.display.display_string("ACCESS DENIED")
        self.buzzer.access_denied_tone()
        self.safe_code.return_to_first_digit()

class UserCode:

    def __init__(self):
        self.user_code = []
        self.user_code_length = 0

    def add_number(self, number: int):
        self.user_code.append(number)
        self.user_code_length = len(self.user_code)


class SafeCode:
    def __init__(self):
        self.safe_code = self.generate_safe_code(self)
        self.current_safe_code_index = 0
        self.current_safe_code_number = self.safe_code[self.current_safe_code_index]

    @staticmethod
    def generate_safe_code(self) -> list:
        safe_code = []
        amount_of_unique_digits = 0
        while amount_of_unique_digits < safe_code_length:
            safe_code = []
            for i in range(0, safe_code_length):
                random_integer = random.randint(1, 19)
                safe_code.append(random_integer)
            amount_of_unique_digits = len(set(safe_code))
        return safe_code

    def next_digit(self):
        max_allowed_index = safe_code_length - 1
        if self.current_safe_code_index < max_allowed_index:
            self.current_safe_code_index += 1
        self.current_safe_code_number = self.safe_code[self.current_safe_code_index]

    def code_complete(self) -> bool:
        max_allowed_index = safe_code_length - 1
        if self.current_safe_code_index == max_allowed_index:
            return True
        else:
            return False

    def is_user_code_correct(self, code) -> bool:
        if code == self.safe_code:
            return True  # User code is correct
        else:
            return False  # User code isn't correct

    def return_to_first_digit(self) -> None:
        self.current_safe_code_index = 0
        self.current_safe_code_number = self.safe_code[self.current_safe_code_index]

class Buzzer:
    def __init__(self):
        GPIO.setup(buzzer_pin, GPIO.OUT)
        GPIO.output(buzzer_pin, GPIO.LOW)
        self.state = False

    def click_sound(self):
        if self.state:
            self.set_buzzer_state(False)
        else:
            self.set_buzzer_state(True)

    def set_buzzer_state(self, state: bool):
        GPIO.output(buzzer_pin, state)
        self.state = state

    def play_frequency(self, frequency: int, duration: float):
        period = 1.0/frequency
        amount_of_periods = duration/period
        for period_number in range(round(amount_of_periods)):
            self.set_buzzer_state(True)
            time.sleep(period/2)
            self.set_buzzer_state(False)
            time.sleep(period/2)
        self.state = False

    def access_granted_tone(self):
        frequency = access_granted_frequency
        duration = access_granted_duration*0.001
        self.play_frequency(frequency, duration)

    def access_denied_tone(self):
        frequency = access_denied_frequency
        duration = access_denied_duration*0.001
        self.play_frequency(frequency, duration)
    def play_jingle(self):
        safesafe_startup_jingle = [
            {"frequency": 800, "duration": 0.2},
            {"frequency": 1200, "duration": 0.4},
            {"frequency": 1000, "duration": 0.2},
            {"frequency": 1500, "duration": 0.4},
            {"frequency": 1200, "duration": 0.2},
            {"frequency": 1600, "duration": 0.4},
            {"frequency": 1400, "duration": 0.2},
            {"frequency": 2000, "duration": 0.4},
            {"frequency": 1800, "duration": 0.2},
        ]

        for note_info in safesafe_startup_jingle:
            note = note_info["frequency"]
            duration = note_info["duration"]
            period_duration = duration/note
            amount_of_periods = round(duration/period_duration)
            for period in range(amount_of_periods):
                self.set_buzzer_state(True)
                time.sleep(period_duration/2)
                self.set_buzzer_state(False)
                time.sleep(period_duration/2)
            time.sleep(0.1)
        self.state = False


class Button:

    def __init__(self, pin):
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


def get_firmware(cracked: bool):
    """
    Gets the SafeSafe firmware
    :param cracked: Returns the cracked firmware if True
    :return:
    """
    if cracked:
        return SafeSafeCrackFirmware()
    else:
        return SafeSafeFirmware()


def main():
    print("starting")

    firmware = get_firmware(False)
    rotary_encoder = firmware.rotary_encoder
    safe_code = firmware.safe_code
    buzzer = firmware.buzzer
    user_code_handler = firmware.user_code_handler

    display = firmware.display
    display_graphics = DisplayGraphics(display)

    firmware.startup_animation()

    last_selected_number = 0
    submit_button = Button(submit_button_pin)

    display_graphics.display_code_progress()
    while True:

        if rotary_encoder.direction_changed_event():

            selected_number = rotary_encoder.selected_number_before_direction_changed
            print(f"user chose {selected_number}")
            user_code_handler.add_number(selected_number)
            safe_code.next_digit()
            user_code_length = user_code_handler.user_code_length
            current_direction = rotary_encoder.current_direction
            display_graphics.display_code_progress(user_code_length, current_direction)
            print("done")

        if submit_button.was_pressed():
            selected_number = rotary_encoder.selected_number
            user_code_handler.add_number(selected_number)
            user_code = user_code_handler.user_code
            if safe_code.is_user_code_correct(user_code):
                print("YOU GUESSED IT")
                user_code_handler = UserCode()
                firmware.access_granted()
            else:
                print("YOU FUCKED IT UP")
                user_code_handler = UserCode()
                firmware.access_denied()

        current_safe_code_number = safe_code.current_safe_code_number
        selected_number = rotary_encoder.selected_number

        if selected_number != last_selected_number:
            print(f"Selected number: {selected_number}")


        if selected_number == current_safe_code_number and selected_number != last_selected_number:
            print("correct")
            buzzer.click_sound()
            print(current_safe_code_number)

        last_selected_number = selected_number
        time.sleep(0.02)


if __name__ == "__main__":
    main()