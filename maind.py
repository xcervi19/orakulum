import shutil
import tempfile
import os
import platform
from patchright.sync_api import sync_playwright

def seznam_search():
    with sync_playwright() as p:
        # Cesty k profilům - macOS compatible
        if platform.system() == "Darwin":  # macOS
            chrome_user_data = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        else:  # Windows
            chrome_user_data = r"C:\Users\cervicek\AppData\Local\Google\Chrome\User Data"
        
        # Vytvoř dočasný adresář pro Playwright Chromium
        temp_user_data = os.path.join(tempfile.gettempdir(), "playwright_chrome_profile")

        print(f"Kopíruji Chrome profil do: {temp_user_data}")
        
        # Smaž starou temp složku, pokud existuje
        if os.path.exists(temp_user_data):
            print("Mažu starou dočasnou složku...")
            try:
                shutil.rmtree(temp_user_data)
            except Exception as e:
                print(f"Varování: {e}")
        
        # Vytvoř novou složku
        os.makedirs(temp_user_data, exist_ok=True)
        
        # Zkopíruj Default profil
        source_profile = os.path.join(chrome_user_data, "Default")
        dest_profile = os.path.join(temp_user_data, "Default")
        
        if os.path.exists(source_profile):
            print("Kopíruji Default profil...")
            os.makedirs(dest_profile, exist_ok=True)
            
            # KLÍČOVÉ SOUBORY PRO PŘIHLÁŠENÍ:
            critical_files = [
                "Cookies",              # Hlavní cookies
                "Cookies-journal",      # Cookies žurnál
                "Network/Cookies",      # Síťové cookies
                "Network/Cookies-journal",
                "Login Data",           # Uložená hesla
                "Login Data-journal",
                "Web Data",             # Autofill data
                "Web Data-journal",
                "Preferences",          # Nastavení prohlížeče
                "Secure Preferences",   # Bezpečnostní nastavení
            ]
            
            # Zkopíruj klíčové soubory
            for file_path in critical_files:
                source_file = os.path.join(source_profile, file_path)
                dest_file = os.path.join(dest_profile, file_path)
                
                if os.path.exists(source_file):
                    # Vytvoř podadresáře pokud je potřeba (např. Network)
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    try:
                        shutil.copy2(source_file, dest_file)
                        print(f"  ✓ {file_path}")
                    except Exception as e:
                        print(f"  ✗ {file_path}: {e}")
            
            # Zkopíruj složky se session daty
            session_folders = [
                "Session Storage",
                "Local Storage", 
                "IndexedDB",
                "Service Worker",
            ]
            
            for folder in session_folders:
                source_folder = os.path.join(source_profile, folder)
                dest_folder = os.path.join(dest_profile, folder)
                
                if os.path.exists(source_folder):
                    try:
                        shutil.copytree(source_folder, dest_folder, dirs_exist_ok=True)
                        print(f"  ✓ {folder}/")
                    except Exception as e:
                        print(f"  ✗ {folder}/: {e}")
        
        # Zkopíruj Local State (důležité pro Chrome)
        local_state_source = os.path.join(chrome_user_data, "Local State")
        local_state_dest = os.path.join(temp_user_data, "Local State")
        
        if os.path.exists(local_state_source):
            try:
                shutil.copy2(local_state_source, local_state_dest)
                print("  ✓ Local State")
            except Exception as e:
                print(f"  ✗ Local State: {e}")
        
        print("\nSpouštím Playwright Chromium s přihlášením...")

        browser = p.chromium.launch_persistent_context(
            chrome_user_data,
            headless=False,
            args=[
                '--profile-directory=Default'
            ]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Tvůj původní kód pokračuje tady...
        page.goto("https://chatgpt.com/")
        print("Seznam.cz načten úspěšně!")
        
        # ... zbytek tvého kódu ...
        page.fill("textarea[name='prompt-textarea']", "jake jsou dove zpravy krelevatni pro vizionare a podnikatele ktery cili na miliardy, skalovani na cely svet")
        page.click("#composer-submit-button")

        input("Stiskni Enter pro ukončení...")
        browser.close()

if __name__ == "__main__":
    print("Používám Chrome User Data pro Playwright Chromium")
    print("Chrome MŮŽE běžet - použijeme kopii profilu")
    print("-" * 50)
    seznam_search()