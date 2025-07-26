from button_action import ButtonAction
import time

# Create buttons
help_button = ButtonAction("Help", "templates/help_button.png")
claim_button = ButtonAction("Claim", "templates/claim_button.png")

while True:
    print("Taking fast screencap...")
    screenshot = help_button.adb_screencap_fast()  # Only call once and reuse!

    help_found = help_button.perform_actions(screenshot)
    claim_found = claim_button.perform_actions(screenshot)
    time.sleep(0.01)

    # Add any additional logic or break condition here
