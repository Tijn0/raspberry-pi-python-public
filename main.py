# SafeSafe: Secure Storage Solutions
import threading
from queue import Queue
import RPi.GPIO as GPIO
import random

import _queue

import code_handler
import logging_manager
import time
import logging

# local imports
import display_manager
import button
import buzzer
import firmware_handler
import rotary_encoder
import servo

# pins configuration
encoder_s1_pin = 26  # s1
encoder_s2_pin = 19  # s2
buzzer_pin = 5  # connected to buzzer +
submit_button_pin = 21
servo_pin = 18

# debounce stuff
button_debounce_time = 100  # milliseconds
rotary_encoder_debounce_time = 100  # milliseconds

# puzzle settings
safe_code_length = 3

# Sound settings
access_granted_frequency = 1000  # Hz
access_granted_duration = 200    # milliseconds

access_denied_frequency = 400    # Hz
access_denied_duration = 300     # milliseconds

# loop settings
display_updater_interval = 0.05

# GPIO setup
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

# Queue setup
queue = Queue()

def current_milli_time():
    return round(time.time() * 1000)

def get_handlers():

    buzzer_handler = buzzer.Buzzer(buzzer_pin, GPIO)
    safe_code_handler = code_handler.SafeCode(safe_code_length)
    display_handler = display_manager.Display()
    rotary_encoder_handler = rotary_encoder.RotaryEncoder(encoder_s1_pin, encoder_s2_pin, GPIO, rotary_encoder_debounce_time)
    servo_handler = servo.Servo(servo_pin, GPIO)
    display_graphics_handler = display_manager.DisplayGraphics(display_handler, safe_code_length)
    submit_button_handler = button.Button(submit_button_pin, GPIO, button_debounce_time)

    return buzzer_handler, safe_code_handler, display_handler, rotary_encoder_handler, servo_handler, display_graphics_handler, submit_button_handler


def display_updater(cracked, display_handler, display_graphics_handler, safe_code_handler, rotary_encoder_handler):
    progress_mode = False
    last_millis = current_milli_time()
    while True:
        millis = current_milli_time()
        if millis - last_millis > 500:
            last_millis = millis

        try:
            task = queue.get(block=False)


            if task == "progress_update":
                progress_mode = True
                user_code_length = safe_code_handler.user_code_length
                current_direction = rotary_encoder_handler.current_direction
                display_graphics_handler.display_code_progress(user_code_length, current_direction)

            elif task == "access_denied":
                progress_mode = False
                display_handler.display_string("ACCESS DENIED")

            elif task == "access_granted":
                progress_mode = False
                display_handler.display_string("ACCESS GRANTED")


            queue.task_done()

        except _queue.Empty:
            pass
        finally:
            time.sleep(display_updater_interval)


def mainloop(firmware, rotary_encoder_handler, submit_button_handler, safe_code_handler):
    firmware.startup_animation()
    queue.put("progress_update")
    last_selected_number = 0
    idle_mode = True
    while True:

        if idle_mode:
            pass

        if rotary_encoder_handler.direction_changed_event():
            firmware.on_rotary_encoder_direction_change()
            queue.put("progress_update")

        if submit_button_handler.was_pressed():
            selected_number = rotary_encoder_handler.selected_number
            safe_code_handler.add_number_to_user_code(selected_number)
            if safe_code_handler.is_user_code_correct():
                firmware.access_granted()
            else:
                firmware.access_denied()

        if rotary_encoder_handler.number_changed_event():
            idle_mode = False
            firmware.on_number_change()
            selected_number = rotary_encoder_handler.selected_number
            if safe_code_handler.is_correct_number(selected_number):
                firmware.hovering_over_correct_number()
            if safe_code_handler.current_safe_code_number == selected_number and safe_code_handler.current_safe_code_index == safe_code_length - 1:
                if safe_code_handler.would_code_be_correct(selected_number):
                    firmware.access_granted()
                else:
                    firmware.access_denied()

        # current_safe_code_number = safe_code.current_safe_code_number
        # selected_number = rotary_encoder.selected_number
        #if selected_number == current_safe_code_number and selected_number != last_selected_number:
            #firmware.hovering_over_correct_number()
        # if safe_code_handler.user_code_current_index == safe_code_length - 2:
        # firmware.access_granted()
        # last_selected_number = selected_number

        time.sleep(0.02)


def main():

    cracked = False

    GPIO.setwarnings(False)
    logging_manager.initialize_logger()
    logging.info("started")
    buzzer_handler, safe_code_handler, display_handler, rotary_encoder_handler, servo_handler, display_graphics_handler, submit_button_handler = get_handlers()

    firmware = firmware_handler.get_firmware(cracked, buzzer_handler, safe_code_handler, display_handler, rotary_encoder_handler, servo_handler, display_graphics_handler, queue)

    thread_1 = threading.Thread(target=mainloop, args=(firmware, rotary_encoder_handler, submit_button_handler, safe_code_handler))
    thread_2 = threading.Thread(target=display_updater, args=(cracked, display_handler, display_graphics_handler, safe_code_handler, rotary_encoder_handler))
    thread_1.start()
    thread_2.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
