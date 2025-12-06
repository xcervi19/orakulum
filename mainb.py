import os
import json
import platform
import time
from collections import deque
from pathlib import Path

import cv2
import mss
import numpy as np
import pyautogui
import pyperclip
import tomllib
from jinja2 import Environment, BaseLoader

WAIT_OPEN = 1
AFTER_ENTER = 1
SCROLL_DELAY = 2
FIND_THRESHOLD = 0.9
LOADING_THRESHOLD = 0.9
MONITOR = 0

TEXTAREA_IMG = Path("buttons/textarea.png")
COPY_IMG = Path("buttons/copy.png")
SCROLL_IMG = Path("buttons/scroll.png")
LOADING_IMG = Path("buttons/loading.png")
BOTTOM_AREA = Path("buttons/is_down.png")

DATA_TXT = Path("data.txt")
PROMPTS_TOML = Path("prompts.toml")
DATA_JSON = Path("data.json")

# CLIENT_INPUT = "Už dlouho se učím JS a chtěl bych být frontend dev."
# POSITION_NAME= "Frontend Developer"

CLIENT_INPUT = "Digitalni marketing a grafik"
POSITION_NAME= "grafik"

def save_as_json(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def normalize(x):
    return json.loads(x) if isinstance(x, str) else x


def render(previous_response):
    return previous_response["suggestion"]


def children(x):
    x = normalize(x)
    return [render(x)]
 

def send_text(text):
    pyperclip.copy(text)
    time.sleep(0.1)
    mod = "command" if platform.system() == "Darwin" else "ctrl"
    pyautogui.hotkey(mod, "v")

def find_treshold(image_path, threshold=FIND_THRESHOLD, monitor=MONITOR):
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = template.shape[:2]
    pyautogui.FAILSAFE = False
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[monitor]))
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        return max_val

def find_and_click(image_path, threshold=FIND_THRESHOLD, monitor=MONITOR):
    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    h, w = template.shape[:2]
    pyautogui.FAILSAFE = False
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[monitor]))
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        print(image_path)
        print(max_val)
        if max_val >= threshold:
            x = max_loc[0] + w // 2
            y = max_loc[1] + h // 2
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click()
            return True
    return False

def is_loading(threshold=LOADING_THRESHOLD, monitor=MONITOR):
    template = cv2.imread(str(LOADING_IMG), cv2.IMREAD_GRAYSCALE)
    pyautogui.FAILSAFE = False
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[monitor]))
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return max_val > threshold

def is_really_bottom(threshold=LOADING_THRESHOLD, monitor=MONITOR):
    template = cv2.imread(str(BOTTOM_AREA), cv2.IMREAD_GRAYSCALE)
    pyautogui.FAILSAFE = False
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[monitor]))
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        return max_val > threshold

def wait_until_loaded(poll=1):
    time.sleep(AFTER_ENTER)
    while is_loading():
        time.sleep(poll)
         
def click_scroll_copy():
    if not is_really_bottom():
        print("scrolling")
        find_and_click(str(SCROLL_IMG))
        time.sleep(SCROLL_DELAY)
    find_and_click(str(COPY_IMG))
    return pyperclip.paste()


def send_and_get(payload):
    time.sleep(WAIT_OPEN)
    find_and_click(str(TEXTAREA_IMG))
    send_text(payload)
    pyautogui.press("enter")
    wait_until_loaded()
    return click_scroll_copy()


def send_and_get_summary(summary_prompt):
    time.sleep(WAIT_OPEN)
    find_and_click(str(TEXTAREA_IMG))
    send_text(summary_prompt)
    pyautogui.press("enter")
    wait_until_loaded()
    return click_scroll_copy()


def jinja_env():
    return Environment(loader=BaseLoader(), variable_start_string="[[", variable_end_string="]]")


def fill_next_prompt(env, main_prompt, position_name, position_description, summary, suggestion):
    return env.from_string(main_prompt).render(
        dreamrole=position_name,
        clientinput=position_description,
        llmcontext_init=summary,
        llmsuggestion_init=suggestion,
    )

def collect_position_prompt(env, prompt, position_name):
    return env.from_string(prompt).render(
        rawinput=position_name,
    )

def collect_starting_prompt(env, main_prompt, input_text, position_name, llmcontext_init, llmsuggestion_init):
    return env.from_string(main_prompt).render(
        dreamrole=position_name,
        clientinput=input_text,
        llmcontext_init=llmcontext_init,
        llmsuggestion_init=llmsuggestion_init,
    )


def load_prompts(path=PROMPTS_TOML):
    with open(path, "rb") as f:
        data = tomllib.load(f)
    p = data["prompts"]
    return p["main"], p["raw_input"], p["raw_input_json"], p["llmcontext_init"], p["llmsuggestion_init"], p["summary"]

def load_position_name(path=DATA_JSON):
    if not path.exists():
        raise FileNotFoundError("data.json with vysnena_pozice.nazev_pozice is required")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["vysnena_pozice"]["nazev_pozice"]

def save_result_step(result, step_name, depth=0, is_raw=False):
    if is_raw: # raw text not json
        result = {"result": result}
    os.makedirs('results', exist_ok=True)
    with open(f'results/{depth}_{step_name}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f)

def run_prompt(payload, open_hotkey=("ctrl","shift","o"), pre_delay=1, scroll_pause=3):
    time.sleep(pre_delay)
    pyautogui.hotkey(*open_hotkey)
    time.sleep(pre_delay)
    if find_and_click(str(TEXTAREA_IMG)):
        send_text(payload)
    time.sleep(pre_delay)
    pyautogui.press("enter")
    wait_until_loaded()
    find_and_click(str(SCROLL_IMG))
    time.sleep(scroll_pause)
    find_and_click(str(COPY_IMG))
    return pyperclip.paste()

def process(root, summary_prompt, env, main_prompt, position_name, position_description, max_depth=5, max_tries=3):
    attempts = max_tries
    pages = []
    q = deque([(c, 0) for c in children(root)])
    while q:
        node, depth = q.popleft()
        summary = send_and_get_summary(summary_prompt)
        next_prompt = fill_next_prompt(env, main_prompt, position_name, position_description, summary, node)
        print("depth >>>>")
        print(depth)
        resp = send_and_get(next_prompt)
        print("resp >>>>>>>>")
        print(resp)
        resp = normalize(resp)
        elements = resp.get("elements")
        c = resp.get("suggestion")
        # while True:
        #     try:
        #         resp = send_and_get(next_prompt)
        #         print("resp >>>>>>>>")
        #         print(resp)
        #         resp = normalize(resp)
        #         elements = resp.get("elements")
        #         c = resp.get("suggestion")
        #         break
        #     except Exception as e:
        #         print(type(e).__name__, str(e))
        #         attempts -= 1
        #         if attempts == 0:
        #             raise

        save_result_step(resp, "process", depth)
        pages.append(elements)
        if max_depth is not None and depth >= max_depth:
            break
        q.append((c, depth + 1))

    return {"pages": pages}

def main(
    wait_open=WAIT_OPEN,
    after_enter=AFTER_ENTER,
    scroll_delay=SCROLL_DELAY,
    find_threshold=FIND_THRESHOLD, 
    loading_threshold=LOADING_THRESHOLD,
    monitor=MONITOR,
    clientinput=CLIENT_INPUT,
    position_name=POSITION_NAME
):
    global WAIT_OPEN, AFTER_ENTER, SCROLL_DELAY
    global FIND_THRESHOLD, LOADING_THRESHOLD, MONITOR
    WAIT_OPEN = wait_open
    AFTER_ENTER = after_enter
    SCROLL_DELAY = scroll_delay
    globals()["FIND_THRESHOLD"] = find_threshold
    globals()["LOADING_THRESHOLD"] = loading_threshold
    globals()["MONITOR"] = monitor

    main_prompt, raw_input, _, llmcontext_init, llmsuggestion_init, summary_prompt = load_prompts()
    env = jinja_env()

    position_description = run_prompt(collect_position_prompt(env, raw_input, clientinput))
    response = run_prompt(collect_starting_prompt(env, main_prompt, position_description, position_name, llmcontext_init, llmsuggestion_init))
    result = process(response, summary_prompt, env, main_prompt, position_name, position_description, max_depth=6, max_tries=3)
    save_as_json(result, "result.json")


if __name__ == "__main__":
    main()

