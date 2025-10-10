from playwright.sync_api import sync_playwright
from pathlib import Path

PROFILE="profiles/worker_main"
URL="https://corporate.example.com/app"
LOGIN_HINT="input[type=password]"

Path(PROFILE).mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(user_data_dir=PROFILE, channel="chrome", headless=False)
    page=ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=180000)
    needs_login=page.locator(LOGIN_HINT).count()>0 or "login" in page.url.lower()
    if needs_login: input()
    ctx.close()
