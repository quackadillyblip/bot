import subprocess
import numpy as np
import cv2
import time
import os

class ButtonAction:
    def __init__(self, name, template_path, adb_device_id=None):
        self.name = name
        self.template_path = template_path
        self.possible_positions = []
        self.adb_device_id = adb_device_id

    def adb_screencap_fast(self):
        command = ["adb"]
        if self.adb_device_id:
            command += ["-s", self.adb_device_id]
        command += ["exec-out", "screencap", "-p"]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=0x08000000  # Suppress console on Windows
        )
        img_array = np.frombuffer(result.stdout, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img

    def find_button_position(self, img, threshold=0.85):
        template = cv2.imread(self.template_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"[{self.name}] Failed to load template at {self.template_path}")
            return None

        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

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
                self.possible_positions.append(pt)  # Save for future faster searches
                return pt
            else:
                return None

    def adb_tap(self, x, y):
        command = ["adb"]
        if self.adb_device_id:
            command += ["-s", self.adb_device_id]
        command += ["shell", "input", "tap", str(x), str(y)]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)

    def perform_actions(self, img):
        start_time = time.time()

        pt = self.find_button_position(img)
        if pt:
            print(f"[{self.name}] Found at {pt}, clicking...")
            self.adb_tap(pt[0], pt[1])
            elapsed = round((time.time() - start_time)*1000)
            print(f"[{self.name}] Action completed in {elapsed} ms")
            return True
        else:
            print(f"[{self.name}] Not found.")
            return False
