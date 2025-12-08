"""
Automated ChatGPT content generation using pyautogui.
Processes prompts from stage_2_prepared_html/ and saves outputs to stage_3_generated_html/
"""

import cv2
import numpy as np
import mss
import pyautogui
import pyperclip
import platform
import time
import sys
import re
from pathlib import Path
from typing import Optional, Tuple

# Configuration
INPUT_DIR = Path("stage_2_prepared_html")
OUTPUT_DIR = Path("stage_3_generated_html")
BUTTONS_DIR = Path("buttons")

# Button image paths
TEXTAREA_BUTTON = BUTTONS_DIR / "textarea.png"
SEND_BUTTON = BUTTONS_DIR / "firebutton.png"
COPY_BUTTON = BUTTONS_DIR / "copy.png"
STOP_BUTTON = BUTTONS_DIR / "stoper.png"  # "Stop generating" button
SCROLL_BUTTON = BUTTONS_DIR / "scroll.png"  # Scroll button
NEW_CHAT_BUTTON = BUTTONS_DIR / "new.png"  # Optional: for starting new chats

# Timing configuration
WAIT_AFTER_CLICK = 0.5
WAIT_AFTER_PASTE = 0.3
WAIT_FOR_RESPONSE = 30  # Initial wait for response
WAIT_FOR_COPY = 2
MAX_RESPONSE_WAIT = 120  # Maximum time to wait for response
CHECK_INTERVAL = 2  # Check every N seconds if response is ready

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2

# Monitor configuration (0 = primary, 1 = secondary, etc.)
MONITOR = 0


def send_text(text: str) -> bool:
    """Copy text to clipboard and paste it using keyboard shortcut."""
    try:
        pyperclip.copy(text)
        time.sleep(WAIT_AFTER_PASTE)
        mod = "command" if platform.system() == "Darwin" else "ctrl"
        pyautogui.hotkey(mod, "v")
        time.sleep(WAIT_AFTER_PASTE)
        return True
    except Exception as e:
        print(f"   ❌ Error sending text: {e}")
        return False


def find_button(image_path: Path, threshold: float = 0.8, monitor: int = 0) -> bool:
    """
    Check if button image exists on screen (without clicking).
    Returns True if button is found, False otherwise.
    """
    if not image_path.exists():
        return False
    
    template = cv2.imread(str(image_path), 0)  # Read as grayscale
    if template is None:
        return False
    
    try:
        with mss.mss() as sct:
            full = sct.monitors[0]
            mon = sct.monitors[monitor]
            img = np.array(sct.grab(mon))
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        
        return max_val >= threshold
    except:
        return False


def find_and_click(image_path: Path, threshold: float = 0.8, monitor: int = 0, retries: int = 3) -> bool:
    """
    Find button image on screen and click it.
    Uses template matching with multiple threshold attempts.
    """
    if not image_path.exists():
        print(f"   ⚠️  Button image not found: {image_path}")
        return False
    
    template = cv2.imread(str(image_path), 0)  # Read as grayscale
    if template is None:
        print(f"   ⚠️  Could not read image: {image_path}")
        return False
    
    pyautogui.FAILSAFE = False
    
    # Try with decreasing thresholds if first attempt fails
    thresholds = [threshold, threshold - 0.1, threshold - 0.2, 0.6]
    
    for attempt_threshold in thresholds:
        try:
            with mss.mss() as sct:
                full = sct.monitors[0]
                mon = sct.monitors[monitor]
                img = np.array(sct.grab(mon))
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            
            if max_val >= attempt_threshold:
                h, w = template.shape[:2]
                cx = max_loc[0] + w // 2
                cy = max_loc[1] + h // 2
                x = mon['left'] + cx
                y = mon['top'] + cy
                sw, sh = pyautogui.size()
                sx = sw / full['width']
                sy = sh / full['height']
                
                pyautogui.moveTo(int(x * sx), int(y * sy), duration=0.1)
                time.sleep(0.1)
                pyautogui.click()
                time.sleep(WAIT_AFTER_CLICK)
                return True
        except Exception as e:
            if attempt_threshold == thresholds[-1]:  # Last attempt
                print(f"   ❌ Error finding button: {e}")
            continue
    
    return False


def wait_for_response(max_wait: int = MAX_RESPONSE_WAIT) -> bool:
    """
    Wait for ChatGPT to finish generating response.
    Checks if "Stop generating" button exists - if it does, still generating.
    When button disappears, generation is complete.
    """
    print(f"   ⏳ Waiting for response (max {max_wait}s)...")
    start_time = time.time()
    
    # Wait a bit first - response needs time to start
    time.sleep(2)
    
    while time.time() - start_time < max_wait:
        # Check if "Stop generating" button exists
        is_generating = find_button(STOP_BUTTON, threshold=0.7, monitor=MONITOR)
        
        if not is_generating:
            # Button not found - generation is complete
            print(f"   ✅ Response complete (stop button disappeared)")
            return True
        
        # Still generating, wait a bit more
        time.sleep(CHECK_INTERVAL)
    
    print(f"   ⏱️  Max wait time reached, assuming complete")
    return True


def process_single_prompt(prompt_text: str, prompt_name: str) -> Optional[str]:
    """
    Process a single prompt through ChatGPT and return the response.
    Returns the response text or None if failed.
    """
    print(f"\n📝 Processing: {prompt_name}")
    
    # Step 1: Find and click textarea
    print("   🔍 Looking for textarea...")
    if not find_and_click(TEXTAREA_BUTTON, threshold=0.7, monitor=MONITOR):
        print("   ❌ Could not find textarea")
        return None
    
    # Step 2: Clear any existing text and paste prompt
    print("   📋 Pasting prompt...")
    # Select all - use command on Mac, ctrl on Windows/Linux
    select_all_key = "command" if platform.system() == "Darwin" else "ctrl"
    pyautogui.hotkey(select_all_key, "a")
    time.sleep(0.2)
    
    if not send_text(prompt_text):
        print("   ❌ Failed to paste prompt")
        return None
    
    # Step 3: Click send button
    print("   🚀 Sending prompt...")
    if not find_and_click(SEND_BUTTON, threshold=0.7, monitor=MONITOR):
        print("   ❌ Could not find send button")
        return None
    
    # Step 4: Wait for response to complete
    wait_for_response()
    
    # Step 5: Scroll down to reveal copy button
    print("   📜 Scrolling to reveal copy button...")
    time.sleep(1)  # Small delay after generation completes
    
    # Try to find and click scroll button
    if find_and_click(SCROLL_BUTTON, threshold=0.7, monitor=MONITOR):
        time.sleep(1)  # Wait for scroll to complete
    else:
        # Fallback: use keyboard scroll (Page Down or arrow keys)
        print("   ⚠️  Scroll button not found, using keyboard scroll...")
        pyautogui.press('pagedown')
        time.sleep(1)
    
    # Step 6: Find and click copy button (must use button, not keyboard shortcut)
    print("   📋 Copying response using copy button...")
    time.sleep(WAIT_FOR_COPY)
    
    if not find_and_click(COPY_BUTTON, threshold=0.7, monitor=MONITOR):
        print("   ❌ Could not find copy button")
        return None
    
    # Wait a moment for clipboard to update
    time.sleep(0.5)
    response = pyperclip.paste()
    
    if not response or len(response.strip()) < 10:
        print("   ❌ Failed to copy response or response too short")
        return None
    
    print(f"   ✅ Got response ({len(response)} chars)")
    return response


def extract_number_from_filename(filename: str) -> Optional[int]:
    """Extract number from filename like 'part1.txt' -> 1, 'part12.txt' -> 12"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else None


def get_output_filename(input_filename: str) -> str:
    """Generate output filename from input filename: part1.txt -> parthtml1.txt"""
    number = extract_number_from_filename(input_filename)
    if number is not None:
        return f"parthtml{number}.txt"
    else:
        # Fallback: use input filename with parthtml prefix
        stem = Path(input_filename).stem
        return f"parthtml_{stem}.txt"


def process_all_prompts():
    """Process all prompt files from INPUT_DIR and save to OUTPUT_DIR"""
    
    # Ensure directories exist
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Get all .txt files from input directory
    prompt_files = sorted(INPUT_DIR.glob("*.txt"))
    
    if not prompt_files:
        print(f"❌ No .txt files found in {INPUT_DIR}")
        return
    
    print(f"📁 Found {len(prompt_files)} prompt files")
    print(f"📂 Input: {INPUT_DIR}")
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"\n⏸️  Make sure ChatGPT is open and visible on monitor {MONITOR}")
    print("⏸️  Starting in 5 seconds...")
    time.sleep(5)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for prompt_file in prompt_files:
        # Check if output already exists
        output_filename = get_output_filename(prompt_file.name)
        output_path = OUTPUT_DIR / output_filename
        
        if output_path.exists():
            print(f"\n⏭️  Skipping {prompt_file.name} (output already exists: {output_filename})")
            skipped += 1
            continue
        
        # Read prompt
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_text = f.read().strip()
        except Exception as e:
            print(f"\n❌ Error reading {prompt_file.name}: {e}")
            failed += 1
            continue
        
        if not prompt_text:
            print(f"\n⚠️  {prompt_file.name} is empty, skipping")
            skipped += 1
            continue
        
        # Process prompt with retries
        response = None
        for attempt in range(MAX_RETRIES):
            if attempt > 0:
                print(f"   🔄 Retry attempt {attempt + 1}/{MAX_RETRIES}")
                time.sleep(RETRY_DELAY)
            
            response = process_single_prompt(prompt_text, prompt_file.name)
            if response:
                break
        
        if response:
            # Save response
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response)
                print(f"   💾 Saved to {output_filename}")
                successful += 1
            except Exception as e:
                print(f"   ❌ Error saving to {output_path}: {e}")
                failed += 1
        else:
            print(f"   ❌ Failed to get response after {MAX_RETRIES} attempts")
            failed += 1
        
        # Delay between prompts to avoid rate limits
        if prompt_file != prompt_files[-1]:  # Not the last file
            print(f"   ⏸️  Waiting 3 seconds before next prompt...")
            time.sleep(3)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✨ Processing complete!")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   📊 Total: {len(prompt_files)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    try:
        process_all_prompts()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

