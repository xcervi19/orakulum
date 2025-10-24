import time,cv2,numpy as np,pyautogui,mss
from pathlib import Path
import tomllib
import psycopg2
from psycopg2.extras import Json
import platform, pyautogui, pyperclip
from dotenv import load_dotenv
load_dotenv()
import os
from db import ConversationDB
from jinja2 import Environment, BaseLoader
from expander import auto_expand
import json
import asyncio
from expander import expand
from collections import deque

WAIT_OPEN=1
AFTER_ENTER=1
SCROLL_DELAY=2
LOAD_TIMEOUT=600
RETRIES=3


def _normalize(x):
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            return x
    return x

def _children(x):
    x=_normalize(x)
    try:
        return list(expand(x))[:1]
    except:
        return []

def _render(child):
    filled_user_input = env.from_string(user_input).render(clientinput=json.dumps(child, indent=2, ensure_ascii=False))
    full_prompt = env.from_string(setup).render(user_input=filled_user_input)
    return full_prompt

def _send_and_get(child):
    pyautogui.hotkey('ctrl', 'shift', 'o')
    time.sleep(WAIT_OPEN)
    find_and_click(str(textarea))
    send_text(_render(child))
    pyautogui.press('enter')
    time.sleep(AFTER_ENTER)
    while is_loading():
        print("loading")

    find_and_click(str(scroll))
    time.sleep(SCROLL_DELAY)
    find_and_click(str(copybutton))
    resp=pyperclip.paste()
    return _normalize(resp)

    return None

def process(root, max_depth=None):
    q=deque((c,0) for c in _children(root))
    while q:
        node,depth=q.popleft()
        if max_depth is not None and depth>=max_depth:
            continue
        print(node)
        print("--------------------------------")
        resp=_send_and_get(node)
        # print("responce")
        # print(resp)
        if resp is None:
            continue

        for c in _children(resp):
            print("_children(resp)")
            print(c)
            q.append((c,depth+1))


with open('data.json') as f:
    data_adhoc_json = json.load(f)

with open('data.txt') as f:
    position_description = f.read()

# db = ConversationDB()
# db.connect()
# conversation_id = db.create_conversation("Test Conversation")

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
loading = Path("buttons/loading.png")
clientinput = "Už dlouho se učím JS a chtěl bych být frontend dev."

raw_input_json_filled = raw_input_json.format(rawinput=clientinput)
raw_input_filled = raw_input.format(rawinput=clientinput)


env = Environment(loader=BaseLoader(), variable_start_string='[[', variable_end_string=']]')


def collect_starting_prompt(input, position_name, companies):
    filled_user_input = env.from_string(user_input).render(
        dreamrole=position_name,
        targetcompanies=companies,
        clientinput=input
    )

    full_prompt = env.from_string(setup).render(user_input=filled_user_input)
    return full_prompt

def send_text(text: str):
    pyperclip.copy(text)
    time.sleep(0.1)
    mod = "command" if platform.system()=="Darwin" else "ctrl"
    pyautogui.hotkey(mod, "v")

def find_and_click(image_path,threshold=0.6,monitor=0):
    template=cv2.imread(image_path,cv2.IMREAD_GRAYSCALE)
    h,w=template.shape[:2]
    pyautogui.FAILSAFE=False
    with mss.mss() as sct:
        img=np.array(sct.grab(sct.monitors[monitor]))
        gray=cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)
        cv2.imwrite('debug2.png', gray)
        cv2.imwrite('debug.png', template)
        res=cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
        _,max_val,_,max_loc=cv2.minMaxLoc(res)
        print(image_path)
        print(max_val)
        if max_val>=threshold:
            x=max_loc[0]+w//2
            y=max_loc[1]+h//2
            pyautogui.moveTo(x,y,duration=0.1)
            pyautogui.click()
            return True
        time.sleep(0.2)

def is_loading(threshold=0.90,monitor=0):
    template=cv2.imread(str(loading),cv2.IMREAD_GRAYSCALE)
    h,w=template.shape[:2]
    pyautogui.FAILSAFE=False
    with mss.mss() as sct:
        img=np.array(sct.grab(sct.monitors[monitor]))
        gray=cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)
        res=cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
        _,max_val,_,max_loc=cv2.minMaxLoc(res)
        print("max_val is_loading")
        print(max_val)
        if max_val > threshold:
            print("KONEC CEKANI")
            return True
        time.sleep(1)

if __name__=="__main__":
    # if find_and_click(str(textarea)):
    #     send_text(raw_input_filled)
    # pyautogui.press('enter')
    # print("fired")
    # while is_loading():
    #     print("loading")
    # if find_and_click(str(scroll)):
    #     print("scrolled")
    # time.sleep(3)
    # if find_and_click(str(copybutton)):
    #     print("copied")
    # position_description = pyperclip.paste()
    # print(position_description)
    
    # pyautogui.hotkey('ctrl', 'shift', 'o')
    # time.sleep(2)
    # if find_and_click(str(textarea)):
    #     send_text(raw_input_json_filled)
    # pyautogui.press('enter')
    # while is_loading():
    #     print("loading")
    # if find_and_click(str(scroll)):
    #     print("scrolled")
    # time.sleep(3)
    # if find_and_click(str(copybutton)):
    #     print("copied")
    # position_data = pyperclip.paste()
    # print(position_data)
    # db.create_conversation_root(conversation_id, "system", "initialization", json_data=position_data, text_data=position_description)

    # pyautogui.hotkey('ctrl', 'shift', 'o')
    # time.sleep(1)
    # if find_and_click(str(textarea)):
    #     position_name = data_adhoc_json['vysnena_pozice']['nazev_pozice']
    #     companies = data_adhoc_json['doporucene_firmy'] 
    #     send_text(collect_starting_prompt(position_description, position_name, companies))
    # time.sleep(1)
    # pyautogui.press('enter')
    # while is_loading():
    #     print("loading")
    # if find_and_click(str(scroll)):
    #     print("scrolled")
    # time.sleep(3)
    # if find_and_click(str(copybutton)):
    #     print("copied")
    # response = pyperclip.paste()
    # db.create_conversation_root(conversation_id, "system", "initialization", json_data=response)

    with open('check.json', encoding='utf-8') as f:
        initial_screen = json.load(f)
    time.sleep(2)

    process(initial_screen, max_depth=None)

    # db.disconnect()


