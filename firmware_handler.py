import logging
import time


def get_firmware(cracked: bool, buzzer, safe_code, display, rotary_encoder, lock, display_graphics, queue):
    """
    Gets the SafeSafe firmware
    :param cracked: Returns the cracked firmware if True
    :return:
    """
    if cracked:
        logging.info("Getting SafeSafeCrack Firmware")
        return SafeSafeCrackFirmware(buzzer, safe_code, display, rotary_encoder, lock, display_graphics, queue)
    else:
        logging.info("Getting SafeSafe Firmware")
        return SafeSafeFirmware(buzzer, safe_code, display, rotary_encoder, lock, display_graphics, queue)


class SafeSafeFirmware:
    def __init__(self, buzzer, safe_code, display, rotary_encoder, lock, display_graphics, queue):
        self.queue = queue
        self.buzzer = buzzer
        self.safe_code = safe_code
        self.display = display
        self.rotary_encoder = rotary_encoder
        self.lock = lock
        self.display_graphics = display_graphics

    def startup_animation(self) -> None:

        message = "Starting SafeSafe!"
        dots = []
        for i in range(0, 1):
            [dots.append(i) for i in range(1, 4)]
        self.display.display_string(f"SafeSafe OS", clear_display_first=True)
        self.display.display_string(f"Booting", clear_display_first=False, row=2)
        for amount in dots:
            self.display.display_string(('.' * amount)+(3-amount)*" ", row=2, column=7, clear_display_first=False)
            time.sleep(1)
        self.display.clear_display()
        #self.buzzer.play_jingle()

    def access_granted(self) -> None:
        logging.info("ACCESS GRANTED")
        self.queue.put("access_granted")
        self.buzzer.access_granted_tone()
        self.safe_code.reset_progress()
        self.lock.unlock()

    def generate_new_safe_code(self) -> None:
        self.safe_code.reset_progress()
        self.safe_code.safe_code = self.safe_code.generate_safe_code()
        self.safe_code.reset_progress()

    def access_denied(self) -> None:
        logging.info("ACCESS DENIED")
        self.queue.put("access_denied")
        self.buzzer.access_denied_tone()
        self.safe_code.reset_progress()

    def hovering_over_correct_number(self) -> None:
        logging.info(f"CORRECT number selected {self.safe_code.current_safe_code_number}")
        self.buzzer.click_sound()

    def on_number_change(self) -> None:
        selected_number = self.rotary_encoder.selected_number
        logging.info(f"Selected number: {selected_number}")

    def on_rotary_encoder_direction_change(self) -> None:
        selected_number = self.rotary_encoder.selected_number_before_direction_changed
        logging.info(f"user chose {selected_number}")
        self.safe_code.add_number_to_user_code(selected_number)


class SafeSafeCrackFirmware:
    def __init__(self, buzzer, safe_code, display, rotary_encoder, lock, display_graphics, queue):
        self.queue = queue
        self.buzzer = buzzer
        self.safe_code = safe_code
        self.display = display
        self.rotary_encoder = rotary_encoder
        self.lock = lock
        self.display_graphics = display_graphics

    def startup_animation(self) -> None:
        message = "Starting SafeSafe!"
        dots = []
        self.display.display_string(f">Injecting Crack", clear_display_first=True)
        self.display_graphics.display_progress_bar(5)
        self.display.display_string("SafeSafeCrack")
        # for amount in dots:
        # display.display_string(('.' * amount)+(3-amount)*" ", row=2, column=8, clear_display_first=False)
        # time.sleep(1)
        #self.buzzer.play_jingle()

    def access_granted(self) -> None:
        logging.info("ACCESS GRANTED")
        self.queue.put("access_granted")
        self.buzzer.access_granted_tone()
        self.safe_code.reset_progress()
        self.lock.unlock()

    def access_denied(self) -> None:
        logging.info("ACCESS DENIED")
        self.queue.put("access_denied")
        self.buzzer.access_denied_tone()
        self.safe_code.reset_progress()

    def hovering_over_correct_number(self) -> None:
        logging.info(f"CORRECT number selected {self.safe_code.current_safe_code_number}")
        self.buzzer.click_sound()

    def on_number_change(self) -> None:
        selected_number = self.rotary_encoder.selected_number
        logging.info(f"Selected number: {selected_number}")

    def on_rotary_encoder_direction_change(self) -> None:
        selected_number = self.rotary_encoder.selected_number_before_direction_changed
        logging.info(f"user chose {selected_number}")
        self.safe_code.add_number_to_user_code(selected_number)
