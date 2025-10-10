import os
from patchright.sync_api import sync_playwright

def chatgpt_automation():
    # Vytvoř trvalý profil jen pro Playwright (oddělený od Chrome)
    playwright_profile = os.path.join(os.path.expanduser("~"), "playwright_chatgpt_profile")
    
    with sync_playwright() as p:
        print(f"Používám Playwright profil: {playwright_profile}")
        
        browser = p.chromium.launch_persistent_context(
            playwright_profile,
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("Otevírám ChatGPT...")
        page.goto("https://chatgpt.com/", wait_until="networkidle")
        
        # Počkej 3 sekundy
        page.wait_for_timeout(3000)
        
        # Zkontroluj jestli existuje textarea (= jsi přihlášený)
        try:
            page.wait_for_selector("textarea[id='prompt-textarea']", timeout=5000)
            print("✓ Jsi přihlášený! Odesílám zprávu...")
            
            # Vyplň a odešli zprávu
            page.fill("textarea[id='prompt-textarea']", 
                     "jake jsou dove zpravy krelevatni pro vizionare a podnikatele ktery cili na miliardy, skalovani na cely svet")
            page.click("button[data-testid='send-button']")
            
            print("✓ Zpráva odeslána!")
            
        except Exception as e:
            print(f"⚠ Nejsi přihlášený!")
            print("Přihlas se TERAZ v otevřeném okně.")
            print("Po přihlášení se cookies uloží a příště už budeš přihlášený automaticky.")
        
        input("\nStiskni Enter pro ukončení...")
        browser.close()

if __name__ == "__main__":
    print("=" * 60)
    print("ChatGPT Automation - Playwright vlastní profil")
    print("=" * 60)
    print("První spuštění: Přihlas se manuálně")
    print("Další spuštění: Automaticky přihlášený")
    print("=" * 60)
    chatgpt_automation()