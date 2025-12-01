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


def find_and_click(image_path, threshold=0.8, monitor=0):
    template = cv2.imread(image_path, 0)
    if template is None: return False
    pyautogui.FAILSAFE = False
    with mss.mss() as sct:
        full = sct.monitors[0]
        mon = sct.monitors[monitor]
        img = np.array(sct.grab(mon))
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val < threshold: return False
    h, w = template.shape[:2]
    cx = max_loc[0] + w // 2
    cy = max_loc[1] + h // 2
    x = mon['left'] + cx
    y = mon['top'] + cy
    sw, sh = pyautogui.size()
    sx = sw / full['width']
    sy = sh / full['height']
    pyautogui.moveTo(int(x * sx), int(y * sy), duration=0.05)
    pyautogui.click()
    return True





if __name__=="__main__":
    time.sleep(2)
    print("🚀 Starting Orakulum automation script...")
    
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
        if find_and_click(str(firebutton)):
            print("📝 Found textarea, sending text...")
            send_text(filled)
        else:
            print("❌ Could not find textarea")
        time.sleep(3)
        
        # print("📜 Scrolling...")
        # find_and_click(str(scroll))
        # time.sleep(1)
        
        # print("📋 Copying result...")
        # find_and_click(str(copybutton))
        # data = pyperclip.paste()
        # print("✅ Result copied to clipboard:")
        # print(data)
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        sys.exit(1)