# Orakulum - macOS Setup Guide

This guide will help you get the Orakulum automation script working on macOS.

## Quick Start

1. **Run the setup script:**
   ```bash
   python3 setup_macos.py
   ```

2. **Grant accessibility permissions:**
   - Go to System Preferences > Security & Privacy > Privacy
   - Select "Accessibility" from the left sidebar
   - Click the lock icon and enter your password
   - Add Terminal (or your Python app) to the list
   - Make sure the checkbox is checked

3. **Run the main script:**
   ```bash
   python3 main.py
   ```

## Manual Setup

If you prefer to set up manually:

1. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   python3 -m playwright install chromium
   ```

4. **Grant accessibility permissions** (see above)

### Alternative: Install without virtual environment

If you prefer to install system-wide (not recommended):

```bash
pip3 install --user -r requirements.txt
# or
pip3 install --break-system-packages -r requirements.txt
```

## Troubleshooting

### "Accessibility permissions required" error
- Make sure you've granted accessibility permissions to Terminal or your Python app
- You can check this in System Preferences > Security & Privacy > Privacy > Accessibility

### "Could not find textarea" error
- Make sure the target website is open and visible
- The script looks for specific button images in the `buttons/` folder
- Make sure these image files exist and match the current website layout

### Playwright errors
- Make sure you've installed Playwright browsers: `python3 -m playwright install chromium`
- For other browsers: `python3 -m playwright install firefox webkit`

## Files Overview

- `main.py` - Main automation script using pyautogui
- `mainb.py` - Playwright-based automation
- `mainc.py` - Async Playwright automation
- `maind.py` - Chrome profile automation
- `setup_macos.py` - macOS setup helper
- `requirements.txt` - Python dependencies

## Notes

- The script uses `command+v` for pasting on macOS (vs `ctrl+v` on Windows)
- Image recognition requires the button images in the `buttons/` folder
- Make sure your screen resolution and website layout match the expected button positions
