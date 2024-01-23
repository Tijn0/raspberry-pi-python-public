import logging
import random


class SafeCode:
    def __init__(self, safe_code_length):
        self.safe_code_length = safe_code_length
        self.user_code = []
        self.user_code_current_index = 0
        self.user_code_length = 0
        self.safe_code = self.generate_safe_code()
        self.current_safe_code_index = 0
        self.current_safe_code_number = self.safe_code[self.current_safe_code_index]

    def generate_safe_code(self) -> list:
        logging.debug("Generating Safe Code!")
        safe_code = []
        amount_of_unique_digits = 0
        while amount_of_unique_digits < self.safe_code_length:
            safe_code = []
            for i in range(0, self.safe_code_length):
                random_integer = random.randint(1, 19)
                safe_code.append(random_integer)
            amount_of_unique_digits = len(set(safe_code))
        logging.debug(f"Safe code: {safe_code}")
        return safe_code

    def next_digit(self) -> None:
        last_digit = self.current_safe_code_number
        max_allowed_index = self.safe_code_length - 1
        if self.current_safe_code_index < max_allowed_index:
            self.current_safe_code_index += 1
        self.current_safe_code_number = self.safe_code[self.current_safe_code_index]

        logging.debug(f"Safe Code next digit ({last_digit} -> {self.current_safe_code_number})")

    def is_user_code_correct(self) -> bool:
        user_code = self.user_code
        safe_code = self.safe_code
        if user_code == safe_code:
            return True  # User code is correct
        else:
            return False  # User code isn't correct

    def reset_progress(self) -> None:
        self.current_safe_code_index = 0
        self.current_safe_code_number = self.safe_code[0]
        self.user_code = []
        self.user_code_current_index = 0
        self.user_code_length = 0

        logging.debug("User Code progress has been reset")

    def would_code_be_correct(self, number: int) -> bool:
        would_be_code = self.user_code + [number]
        print(would_be_code)
        if would_be_code == self.safe_code:
            return True
        else:
            return False

    def add_number_to_user_code(self, number: int) -> None:
        logging.debug(f"SafeCode: added number {number} to user guess")
        self.next_digit()
        self.user_code_length+=1
        self.user_code.append(number)
        self.user_code_current_index += 1

    def is_correct_number(self, number: int) -> bool:
        correct_number = self.current_safe_code_number
        if number == correct_number:
            return True
        else:
            return False
