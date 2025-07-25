from button_action import ButtonAction
import time

class HelpButtonAction(ButtonAction):
    def __init__(self, save_screenshots=False):
        possible_positions = [
            # Add known button positions here if any, e.g. (x, y)
        ]
        super().__init__('templates/button-help.png', 'HelpButton', possible_positions, save_screenshots)

    # You can add extra actions here if needed


if __name__ == "__main__":
    save_screenshots = False
    help_button = HelpButtonAction(save_screenshots=save_screenshots)

    while True:
        found = help_button.perform_actions()
        if found:
            # Additional logic after tap can be placed here
            pass
        time.sleep(0.5)