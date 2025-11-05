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
import json
import asyncio
from expander import expand, extract_context, build_llm_prompt
from collections import deque

WAIT_OPEN=1
AFTER_ENTER=1
SCROLL_DELAY=2
LOAD_TIMEOUT=600
RETRIES=3


def _normalize(x):
    if isinstance(x, str):
        return json.loads(x)
    return x

def _children(x):
    x=_normalize(x)
    return [_render(x)]
    

def _render(previous_response):
    print("--------------------------------")
    print("previous_response")
    print(previous_response)
    print("--------------------------------")
    return previous_response["suggestion"]

def _send_and_get(child):
    time.sleep(WAIT_OPEN)
    find_and_click(str(textarea))
    send_text(child)
    pyautogui.press('enter')
    time.sleep(AFTER_ENTER)
    while is_loading():
        time.sleep(1)

    find_and_click(str(scroll))
    time.sleep(SCROLL_DELAY)
    find_and_click(str(copybutton))
    resp=pyperclip.paste()
    return _normalize(resp)

def _send_and_get_summary():
    time.sleep(WAIT_OPEN)
    find_and_click(str(textarea))
    send_text(summary_prompt)
    pyautogui.press('enter')
    time.sleep(AFTER_ENTER)
    while is_loading():
        time.sleep(1)

    find_and_click(str(scroll))
    time.sleep(SCROLL_DELAY)
    find_and_click(str(copybutton))
    resp=pyperclip.paste()
    return resp

def fill_next_prompt(summary, suggestion):
    position_name = data_adhoc_json['vysnena_pozice']['nazev_pozice']
    full_prompt = env.from_string(main_prompt).render(
        dreamrole=position_name,
        clientinput=position_description,
        llmcontext_init=summary,
        llmsuggestion_init=suggestion
    )
    return full_prompt
    
def process(root, max_depth=5):
    pages = []
    q = deque([(c, 0) for c in _children(root)])
    while q:
        node, depth = q.popleft()
        print("depth")
        print(depth)
        print("--------------------------------")
        print(node)
        print("--------------------------------")
        summary = _send_and_get_summary()
        next_prompt = fill_next_prompt(summary, node)
        print("next_prompt")
        print(next_prompt)
        resp = _send_and_get(next_prompt)
        if resp is None:
            continue
        normalized_resp = _normalize(resp)
        elements = normalized_resp.get("elements") or normalized_resp.get("elemnts")
        if elements:
            pages.append(elements)
        c = normalized_resp.get("suggestion")
        if max_depth is not None and depth >= max_depth:
            break
        q.append((c, depth + 1))
    return {"pages": pages}


with open('data.json') as f:
    data_adhoc_json = json.load(f)

with open('data.txt') as f:
    position_description = f.read()

# db = ConversationDB()
# db.connect()
# conversation_id = db.create_conversation("Test Conversation")

with open("prompts.toml", "rb") as f:
    data = tomllib.load(f)

main_prompt = data["prompts"]["main"]
raw_input = data["prompts"]["raw_input"]
raw_input_json = data["prompts"]["raw_input_json"]
llmcontext_init = data["prompts"]["llmcontext_init"]
llmsuggestion_init = data["prompts"]["llmsuggestion_init"]
summary_prompt = data["prompts"]["summary"]

textarea = Path("buttons/textarea.png")
firebutton = Path("buttons/firebutton.png")
copybutton = Path("buttons/copy.png")
scroll = Path("buttons/scroll.png")
loading = Path("buttons/loading.png")
clientinput = "Už dlouho se učím JS a chtěl bych být frontend dev."

raw_input_json_filled = raw_input_json.format(rawinput=clientinput)
raw_input_filled = raw_input.format(rawinput=clientinput)


env = Environment(loader=BaseLoader(), variable_start_string='[[', variable_end_string=']]')


def collect_starting_prompt(input, position_name, llmcontext_init, llmsuggestion_init):
    full_prompt = env.from_string(main_prompt).render(
        dreamrole=position_name,
        clientinput=input,
        llmcontext_init=llmcontext_init,
        llmsuggestion_init=llmsuggestion_init
    )
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
        # print(image_path)
        # print(max_val)
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
        # print("max_val is_loading")
        # print(max_val)
        if max_val > threshold:
            # print("KONEC CEKANI")
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
    
    
    # time.sleep(1)
    # pyautogui.hotkey('ctrl', 'shift', 'o')
    # time.sleep(1)
    # if find_and_click(str(textarea)):
    #     position_name = data_adhoc_json['vysnena_pozice']['nazev_pozice']
    #     send_text(collect_starting_prompt(position_description, position_name, llmcontext_init, llmsuggestion_init))
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

    # with open('check.json', 'w') as f:
    #     json.dump(response, f)
    # time.sleep(1)

    with open('check.json', encoding='utf-8') as f:
        initial_screen = json.load(f)
    time.sleep(1)
    print(initial_screen)

    pages = process(initial_screen)

    os.makedirs('results', exist_ok=True)
    with open('results/pages.json', 'w', encoding='utf-8') as f:
        json.dump(pages, f)
    # db.disconnect()


