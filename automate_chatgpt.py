#!/usr/bin/env python3
"""
ChatGPT Automation Script

Uses pyautogui to automate sending prompts to ChatGPT and capturing responses.
Processes all prompt files from an input directory and saves responses to output.

Requirements:
- ChatGPT browser window must be open and visible
- Button images in buttons/ folder (textarea.png, firebutton.png, copy.png)

Usage:
    python3 automate_chatgpt.py --input parsed_parts/ --output stage_2_generated_parts/
    python3 automate_chatgpt.py -i stage_2_prepared_html/ -o stage_3_generated_html/
"""

import os
import sys
import time
import argparse
from pathlib import Path

import cv2
import numpy as np
import mss
import pyautogui
import pyperclip


# Button image paths
BUTTONS_DIR = Path("buttons")
TEXTAREA_IMG = BUTTONS_DIR / "textarea.png"
FIRE_BUTTON_IMG = BUTTONS_DIR / "firebutton.png"
COPY_BUTTON_IMG = BUTTONS_DIR / "copy.png"
SCROLL_IMG = BUTTONS_DIR / "scroll.png"

# Timing settings
DELAY_AFTER_PASTE = 0.5
DELAY_AFTER_SEND = 3.0
DELAY_WAIT_RESPONSE = 60.0  # Max wait time for response
DELAY_BETWEEN_PROMPTS = 2.0


def find_and_click(image_path: str, threshold: float = 0.8, monitor: int = 0) -> bool:
    """
    Find an image on screen and click its center.
    
    Args:
        image_path: Path to template image
        threshold: Match confidence threshold (0-1)
        monitor: Monitor index to search
        
    Returns:
        True if found and clicked, False otherwise
    """
    template = cv2.imread(str(image_path), 0)
    if template is None:
        print(f"❌ Could not load image: {image_path}")
        return False
    
    pyautogui.FAILSAFE = False
    
    with mss.mss() as sct:
        full = sct.monitors[0]
        mon = sct.monitors[monitor]
        img = np.array(sct.grab(mon))
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    
    if max_val < threshold:
        return False
    
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


def send_prompt(prompt_text: str) -> bool:
    """
    Send a prompt to ChatGPT by clicking textarea, pasting, and clicking send.
    
    Args:
        prompt_text: The prompt text to send
        
    Returns:
        True if successfully sent, False otherwise
    """
    # Click textarea
    if not find_and_click(str(TEXTAREA_IMG)):
        print("❌ Could not find textarea")
        return False
    
    time.sleep(0.2)
    
    # Paste prompt
    pyperclip.copy(prompt_text)
    pyautogui.hotkey('command', 'v')  # Use 'ctrl', 'v' on Windows/Linux
    
    time.sleep(DELAY_AFTER_PASTE)
    
    # Click send button
    if not find_and_click(str(FIRE_BUTTON_IMG)):
        print("❌ Could not find send button")
        return False
    
    return True


def wait_for_response(timeout: float = DELAY_WAIT_RESPONSE) -> bool:
    """
    Wait for ChatGPT to finish generating response.
    Detects completion by checking if copy button appears.
    
    Args:
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if response completed, False if timeout
    """
    start_time = time.time()
    
    print("   ⏳ Waiting for response...", end="", flush=True)
    
    while time.time() - start_time < timeout:
        # Check if copy button is visible (indicates response complete)
        if find_and_click(str(COPY_BUTTON_IMG), threshold=0.7):
            print(" Done!")
            return True
        
        time.sleep(2)
        print(".", end="", flush=True)
    
    print(" Timeout!")
    return False


def copy_response() -> str:
    """
    Copy the ChatGPT response using the copy button.
    
    Returns:
        The copied response text
    """
    # The copy button was already clicked in wait_for_response
    time.sleep(0.3)
    return pyperclip.paste()


def process_prompt_file(input_file: Path, output_file: Path) -> bool:
    """
    Process a single prompt file: send to ChatGPT and save response.
    
    Args:
        input_file: Path to prompt file
        output_file: Path to save response
        
    Returns:
        True if successful, False otherwise
    """
    # Skip if output already exists
    if output_file.exists():
        print(f"   ⏭️  Skipping (output exists): {output_file.name}")
        return True
    
    # Read prompt
    with open(input_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    print(f"   📤 Sending: {input_file.name}")
    
    # Send prompt
    if not send_prompt(prompt):
        print(f"   ❌ Failed to send: {input_file.name}")
        return False
    
    time.sleep(DELAY_AFTER_SEND)
    
    # Wait for response
    if not wait_for_response():
        print(f"   ❌ Response timeout: {input_file.name}")
        return False
    
    # Copy and save response
    response = copy_response()
    
    if not response or len(response) < 10:
        print(f"   ❌ Empty response: {input_file.name}")
        return False
    
    # Save response
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(response)
    
    print(f"   ✅ Saved: {output_file.name} ({len(response)} chars)")
    
    return True


def process_directory(input_dir: str, output_dir: str, pattern: str = "*.txt") -> dict:
    """
    Process all prompt files in a directory.
    
    Args:
        input_dir: Directory with prompt files
        output_dir: Directory to save responses
        pattern: Glob pattern for input files
        
    Returns:
        Summary dict with counts
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    # Find input files
    files = sorted(input_path.glob(pattern))
    
    if not files:
        print(f"❌ No {pattern} files found in {input_dir}")
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    print(f"\n📁 Found {len(files)} files in {input_dir}")
    print(f"📂 Output directory: {output_dir}")
    print("=" * 60)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {"total": len(files), "success": 0, "failed": 0, "skipped": 0}
    
    for i, input_file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Processing: {input_file.name}")
        
        # Generate output filename
        output_file = output_path / input_file.name
        
        # Check if already processed
        if output_file.exists():
            results["skipped"] += 1
            print(f"   ⏭️  Skipping (output exists)")
            continue
        
        # Process the file
        success = process_prompt_file(input_file, output_file)
        
        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
        
        # Delay between prompts to avoid rate limiting
        if i < len(files):
            time.sleep(DELAY_BETWEEN_PROMPTS)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Automate ChatGPT prompts using pyautogui"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input directory with prompt files"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output directory for responses"
    )
    parser.add_argument(
        "--pattern", "-p",
        default="*.txt",
        help="File pattern to match (default: *.txt)"
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=DELAY_WAIT_RESPONSE,
        help=f"Max wait time for response (default: {DELAY_WAIT_RESPONSE}s)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: verify buttons can be found without sending"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🤖 CHATGPT AUTOMATION")
    print("=" * 60)
    
    # Verify button images exist
    for btn_path in [TEXTAREA_IMG, FIRE_BUTTON_IMG, COPY_BUTTON_IMG]:
        if not btn_path.exists():
            print(f"❌ Button image not found: {btn_path}")
            print("   Please capture button screenshots and save to buttons/")
            sys.exit(1)
    
    if args.test:
        print("\n🔍 Test mode: Checking if buttons can be found...")
        print(f"   Textarea: {'✅' if find_and_click(str(TEXTAREA_IMG)) else '❌'}")
        time.sleep(0.5)
        print(f"   Fire button: {'✅' if find_and_click(str(FIRE_BUTTON_IMG)) else '❌'}")
        return
    
    # Give user time to focus ChatGPT window
    print("\n⚠️  Make sure ChatGPT browser window is visible!")
    print("   Starting in 3 seconds...")
    time.sleep(3)
    
    # Process directory
    global DELAY_WAIT_RESPONSE
    DELAY_WAIT_RESPONSE = args.delay
    
    results = process_directory(args.input, args.output, args.pattern)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"   Total files: {results['total']}")
    print(f"   ✅ Success: {results['success']}")
    print(f"   ⏭️  Skipped: {results['skipped']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
