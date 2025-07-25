import cv2
import numpy as np
import subprocess
import time
import os

class ButtonAction:
    def __init__(self, template_path, name, possible_positions=None, save_screenshots=False):
        self.template_path = template_path
        self.name = name
        self.possible_positions = possible_positions or []
        self.save_screenshots = save_screenshots
        if save_screenshots:
            os.makedirs('screenshots', exist_ok=True)

    def adb_screencap(self, output_path=None):
        if output_path is None:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_path = os.path.join('screenshots', f'screen_{timestamp}.png')
        
        # Always ensure output_path is within screenshots
        if not output_path.startswith('screenshots'):
            output_path = os.path.join('screenshots', output_path)
        
        result = subprocess.run(['adb', 'exec-out', 'screencap', '-p'], stdout=subprocess.PIPE)
        with open(output_path, 'wb') as f:
            f.write(result.stdout)
        
        if self.save_screenshots:
            print(f"[{self.name}] Screenshot saved as {output_path}")
        
        return output_path



    def find_button(self, screen_path, threshold=0.8):
        img = cv2.imread(screen_path)
        template = cv2.imread(self.template_path)

        if img is None:
            print(f"[{self.name}] Error: screenshot {screen_path} could not be loaded.")
            return None
        if template is None:
            print(f"[{self.name}] Error: template {self.template_path} could not be loaded.")
            return None

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        if self.possible_positions:
            for pos in self.possible_positions:
                x, y = pos
                h, w = template_gray.shape

                margin = 20
                x_start = max(x - margin, 0)
                y_start = max(y - margin, 0)
                x_end = min(x + w + margin, img_gray.shape[1])
                y_end = min(y + h + margin, img_gray.shape[0])

                crop_img = img_gray[y_start:y_end, x_start:x_end]
                res = cv2.matchTemplate(crop_img, template_gray, cv2.TM_CCOEFF_NORMED)
                loc = np.where(res >= threshold)
                if len(loc[0]) > 0:
                    pt = (x_start + loc[1][0], y_start + loc[0][0])
                    return pt
            return None
        else:
            res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            if len(loc[0]) > 0:
                pt = (loc[1][0], loc[0][0])
                return pt
            else:
                return None

    def adb_tap(self, x, y):
        subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)])
        print(f"[{self.name}] Tapped at position: ({x}, {y})")

    def perform_actions(self):
        screenshot_path = self.adb_screencap()  # will return full path inside screenshots/
        pos = self.find_button(screenshot_path)
        if pos:
            print(f"[{self.name}] ✅ Button found at {pos}, tapping...")
            self.adb_tap(pos[0], pos[1])
            time.sleep(1)
            return True
        else:
            print(f"[{self.name}] ❌ Button not found.")
            return False
