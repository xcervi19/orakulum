import time
import pyautogui

print("Starting minimal pyautogui mouse test. You have ~20 seconds...")

start_time = time.time()
duration = 20

try:
    while time.time() - start_time < duration:
        # Move to a safe spot
        pyautogui.moveTo(200, 200, duration=0.5)
        time.sleep(1)
        pyautogui.click()
        pyautogui.moveTo(400, 400, duration=0.5)
        time.sleep(1)
        pyautogui.click()
except Exception as e:
    print(f"Error: {e}")

print("Done. Test finished.")
