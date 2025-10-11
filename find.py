import pyautogui
import time

print("Press Ctrl+C to stop.")
try:
    while True:
        x, y = pyautogui.position()
        print(f"Mouse position: ({x}, {y})", end="\r", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopped.")

