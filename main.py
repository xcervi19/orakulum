import cv2, numpy as np, mss, pyautogui, platform, time
from pathlib import Path
import tomllib
import platform, pyautogui, pyperclip
import sys

# if platform.system() == "Windows":
#     from ctypes import windll, c_void_p
    
# def _enable_dpi_awareness():
#     if platform.system() == "Windows":
#         try:
#             windll.user32.SetProcessDpiAwarenessContext(c_void_p(-4))
#         except Exception:
#             try:
#                 windll.shcore.SetProcessDpiAwareness(2)
#             except Exception:
#                 windll.user32.SetProcessDPIAware()

# def _clahe_gray(img):
#     g = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY) if img.shape[-1]==4 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     clahe = cv2.createCLAHE(2.0,(8,8))
#     return clahe.apply(g)

# def find_and_click(image_path, min_inliers=12, monitor=0):
#     _enable_dpi_awareness()
#     t = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     if t is None: return False
#     pyautogui.FAILSAFE = False
#     with mss.mss() as sct:
#         shot = np.array(sct.grab(sct.monitors[monitor]))
#     g = _clahe_gray(shot)
#     orb = cv2.ORB_create(nfeatures=6000, scaleFactor=1.2, nlevels=12, fastThreshold=7)
#     kp1, des1 = orb.detectAndCompute(t, None)
#     kp2, des2 = orb.detectAndCompute(g, None)
#     if des1 is None or des2 is None: return False
#     bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
#     matches = bf.knnMatch(des1, des2, k=2)
#     good = [m for m,n in matches if m.distance < 0.75*n.distance]
#     if len(good) < min_inliers: return False
#     src = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
#     dst = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
#     H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
#     if H is None: return False
#     h,w = t.shape[:2]
#     corners = np.float32([[0,0],[w,0],[w,h],[0,h]]).reshape(-1,1,2)
#     proj = cv2.perspectiveTransform(corners, H)
#     inliers = int(mask.sum()) if mask is not None else 0
#     if inliers < min_inliers: return False
#     cx = int(proj[:,0,0].mean())
#     cy = int(proj[:,0,1].mean())
#     pyautogui.moveTo(cx, cy, duration=0.1)
#     pyautogui.click()
#     return True



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


def find_and_click(image_path, threshold=0.5):
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if template is None: return False
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[1]))
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    print(f"DEBUG: max_val: {max_val}, max_loc: {max_loc}")
    if max_val < threshold: return False
    h, w = template.shape[:2]
    x, y = max_loc[0] + w // 2, max_loc[1] + h // 2
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click()
    return True

# def find_and_click(image_path, threshold=0.6, monitor=0):
#     print(f"DEBUG: Trying to find and click {image_path} with threshold {threshold} on monitor {monitor}")
#     template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     if template is None: return False
#     pyautogui.FAILSAFE = False
#     with mss.mss() as sct:
#         img = np.array(sct.grab(sct.monitors[monitor]))
#     gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
#     edged_screen = cv2.Canny(gray, 50, 150)
#     best = (-1, None, None, None)  # score, loc, (w,h), scale
#     h0, w0 = template.shape[:2]
#     for s in np.linspace(0.5, 2.0, 16):
#         tw, th = int(w0*s), int(h0*s)
#         if tw < 10 or th < 10: continue
#         t = cv2.resize(template, (tw, th), interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
#         edged_t = cv2.Canny(t, 50, 150)
#         res = cv2.matchTemplate(edged_screen, edged_t, cv2.TM_CCOEFF_NORMED)
#         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#         print(f"DEBUG: min_val: {min_val}, max_val: {max_val}, min_loc: {min_loc}, max_loc: {max_loc}")
#         if max_val > best[0]: best = (max_val, max_loc, (tw, th), s)
#     max_val, max_loc, (tw, th), s = best
#     if max_val is None or max_val < threshold: return False
#     x = max_loc[0] + tw//2
#     y = max_loc[1] + th//2
#     pyautogui.moveTo(x, y, duration=0.1)
#     pyautogui.click()
#     return True




if __name__=="__main__":
    time.sleep(2)
    print("🚀 Starting Orakulum automation script...")
    
    # Check macOS permissions first
    if not check_macos_permissions():
        print("❌ Cannot proceed without accessibility permissions.")
        sys.exit(1)
    
    print("✅ Permissions OK, starting automation...")
    time.sleep(2)
    
    try:
        # if find_and_click(str(textarea)):
        #     print("📝 Found textarea, sending text...")
        #     send_text(filled)
        # else:
        #     print("❌ Could not find textarea")
        # time.sleep(3)
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