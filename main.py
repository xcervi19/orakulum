import time,cv2,numpy as np,pyautogui,mss
from pathlib import Path
import tomllib
import platform, pyautogui, pyperclip
import sys

with open("prompts.toml", "rb") as f:
    data = tomllib.load(f)

setup = data["prompts"]["setup"]
user_input = data["prompts"]["user_input"]
raw_input = data["prompts"]["raw_input"]
raw_input_json = data["prompts"]["raw_input_json"]

textarea = Path("buttons/textarea.png")
firebutton = Path("buttons/firebutton.png")
copybutton = Path("buttons/copy.png")
scroll = Path("buttons/scroll.png")

clientinput = "Už dlouho se učím JS a chtěl bych být frontend dev."
print(raw_input_json)
filled = raw_input_json.format(rawinput=clientinput)

def check_macos_permissions():
    """Check if macOS accessibility permissions are granted for pyautogui"""
    if platform.system() == "Darwin":
        try:
            # Try to move mouse to test permissions
            pyautogui.moveTo(100, 100, duration=0.1)
            return True
        except pyautogui.FailSafeException:
            print("⚠️  macOS Accessibility permissions required!")
            print("Please go to: System Preferences > Security & Privacy > Privacy > Accessibility")
            print("Add Terminal or your Python app to the list of allowed applications.")
            return False
    return True

def send_text(text: str):
    pyperclip.copy(text)
    time.sleep(0.1)
    mod = "command" if platform.system() == "Darwin" else "ctrl"
    pyautogui.hotkey(mod, "v")

def find_and_click(image_path, threshold=0.87, monitor=0):
    print(f"DEBUG: Trying to find and click {image_path} with threshold {threshold} on monitor {monitor}")
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"DEBUG: Could not read template image at path: {image_path}")
        return False
    h, w = template.shape[:2]
    pyautogui.FAILSAFE = False
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[monitor]))
        print(f"DEBUG: Screenshot shape: {img.shape}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        print(f"DEBUG: Template shape: {template.shape}, Screenshot(gray) shape: {gray.shape}")
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(f"DEBUG: min_val: {min_val}, max_val: {max_val}, min_loc: {min_loc}, max_loc: {max_loc}")
        if max_val >= threshold:
            x = max_loc[0] + w // 2
            y = max_loc[1] + h // 2
            print(f"Clicking at {x}, {y} (max_val: {max_val})")
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click()
            return True
        else:
            print("DEBUG: No match found above threshold.")
        time.sleep(0.2)
        return False



if __name__=="__main__":
    time.sleep(2)
    find_and_click(str(textarea))
    exit
    print("🚀 Starting Orakulum automation script...")
    
    # Check macOS permissions first
    if not check_macos_permissions():
        print("❌ Cannot proceed without accessibility permissions.")
        sys.exit(1)
    
    print("✅ Permissions OK, starting automation...")
    time.sleep(2)
    
    try:
        if find_and_click(str(textarea)):
            print("📝 Found textarea, sending text...")
            send_text(filled)
        else:
            print("❌ Could not find textarea")
            
        print("🔥 Clicking fire button...")
        find_and_click(str(firebutton))
        time.sleep(10)
        
        print("📜 Scrolling...")
        find_and_click(str(scroll))
        time.sleep(1)
        
        print("📋 Copying result...")
        find_and_click(str(copybutton))
        data = pyperclip.paste()
        print("✅ Result copied to clipboard:")
        print(data)
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        sys.exit(1)