import time
import logging


# sound config
access_granted_frequency = 1000  # Hz
access_granted_duration = 400    # milliseconds

access_denied_frequency = 400    # Hz
access_denied_duration = 300     # milliseconds

shutdown_tone_frequency = 200    # Hz
shutdown_tone_duration = 1000    # milliseconds


class Buzzer:
    def __init__(self, pin, GPIO):
        self.GPIO = GPIO
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        self.state = False

    def click_sound(self):
        if self.state:
            self.set_buzzer_state(False)
        else:
            self.set_buzzer_state(True)

    def set_buzzer_state(self, state: bool):
        self.GPIO.output(self.pin, state)
        self.state = state

    def play_frequency(self, frequency: int, duration: float):
        logging.debug(f"Buzzer at pin {self.pin} Playing {frequency}Hz for {duration} seconds")
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

    def shutdown_tone(self):
        frequency = shutdown_tone_frequency
        duration = shutdown_tone_duration*0.001
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