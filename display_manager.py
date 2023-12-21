import time
import I2C_LCD_driver

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

    def __init__(self, display, safe_code_length):
        self.display = display
        self.safe_code_length = safe_code_length

    def display_progress_bar(self, duration: int, row: int = 2, column: int = 0, clear_display_first: bool=False):
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

    def display_code_progress(self, user_code_length: int = 0, direction: bool = False, row: int = 2, column: int = 0, clear_display_first: bool = False) -> None:
        """
        Prints a little graphic on the LCD that lets you see your progress on the code
        :param user_code_length: how much of the code is already selected
        :param direction: the direction (dial) in which the next number will be selected (True: right, False: left)
        :param row: numbered 1-2 (1: top row)
        :param column: numbered 0-15 (0: first column)
        :param clear_display_first: clears the display of content before displaying the progress indicator
        :return:
        """
        if user_code_length > self.safe_code_length:
            return

        progress_indicator = f"Code: [{user_code_length * '*'}{(self.safe_code_length - user_code_length) * '_'}]"
        self.display.display_string(progress_indicator, row=row, column=column, clear_display_first=clear_display_first)
        if direction:  # Right
            self.display.display_right_arrow()
        else:  # Left
            self.display.display_left_arrow()


class Display:
    def __init__(self):
        self.lcd = I2C_LCD_driver.lcd()
        self.lcd.lcd_load_custom_chars(custom_lcd_characters)

    def display_string(self, string: str, row: int = 1, column: int = 0, clear_display_first: bool = True) -> None:
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