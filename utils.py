from typing import Set


def get_menu_choice(valid_choices: Set) -> str:
    while True:
        choice = input()
        if choice.upper().strip() in valid_choices:
            print('')
            return choice.upper().strip()
        print('Invalid choice. Please enter one of', valid_choices)

