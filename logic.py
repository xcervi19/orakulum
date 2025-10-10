from typing import List, Literal, Optional, TypedDict
from playwright.async_api import Page
import asyncio, random

class Step(TypedDict, total=False):
    action: Literal["goto","type","fill","click","press","upload"]
    selector: Optional[str]
    value: Optional[str]
    wait: Optional[str]
    
TASKS: list[Step] = [
    {"action":"goto","value":"https://chatgpt.com"},
    {"action":"type","selector":"textarea[id='prompt-textarea]","value":"Hello"},
    {"action":"click","selector":"button[data-testid='send-button']"}
]
TIMEOUT=60000

async def pause(a=0.18,b=0.48): await asyncio.sleep(random.uniform(a,b))

async def apply_logic(page: Page, steps: List[Step]):
    for s in steps:
        if s.get("wait"): await page.wait_for_selector(s["wait"], timeout=TIMEOUT)
        a=s["action"]
        if a=="goto":
            await page.goto(s["value"], wait_until="domcontentloaded", timeout=TIMEOUT); await pause()
        elif a=="fill":
            loc=page.locator(s["selector"]); await loc.wait_for(state="visible"); await loc.fill(s.get("value","")); await pause()
        elif a=="type":
            loc=page.locator(s["selector"]); await loc.wait_for(state="visible"); await loc.click()
            for ch in s.get("value",""): await page.keyboard.type(ch, delay=random.randint(30,120))
            await pause()
        elif a=="click":
            loc=page.locator(s["selector"]); await loc.wait_for(state="visible"); box=await loc.bounding_box()
            if box:
                x=box["x"]+box["width"]*random.uniform(0.2,0.8); y=box["y"]+box["height"]*random.uniform(0.2,0.8)
                await page.mouse.move(x,y,steps=random.randint(8,18)); await pause(0.05,0.12); await page.mouse.down(); await pause(0.04,0.1); await page.mouse.up()
            else:
                await loc.click()
            await pause()
        elif a=="press":
            await page.keyboard.press(s["value"]); await pause()
        elif a=="upload":
            await page.locator(s["selector"]).set_input_files(s["value"]); await pause()
