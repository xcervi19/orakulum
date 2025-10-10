import time,cv2,numpy as np,pyautogui,mss
from pathlib import Path
import tomllib
import platform, pyautogui, pyperclip

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

def send_text(text: str):
    pyperclip.copy(text)
    time.sleep(0.1)
    mod = "command" if platform.system()=="Darwin" else "ctrl"
    pyautogui.hotkey(mod, "v")

def find_and_click(image_path,threshold=0.87,monitor=0):
    template=cv2.imread(image_path,cv2.IMREAD_GRAYSCALE)
    h,w=template.shape[:2]
    pyautogui.FAILSAFE=False
    with mss.mss() as sct:
        img=np.array(sct.grab(sct.monitors[monitor]))
        gray=cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)
        res=cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
        _,max_val,_,max_loc=cv2.minMaxLoc(res)
        if max_val>=threshold:
            x=max_loc[0]+w//2
            y=max_loc[1]+h//2
            pyautogui.moveTo(x,y,duration=0.1)
            pyautogui.click()
            return True
        time.sleep(0.2)


if __name__=="__main__":
    time.sleep(2)
    if find_and_click(str(textarea)):
        send_text(filled)
    find_and_click(str(firebutton))
    time.sleep(10)
    find_and_click(str(scroll))
    time.sleep(1)
    find_and_click(str(copybutton))
    data = pyperclip.paste()
    print(data)