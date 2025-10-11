#!/usr/bin/env python3
"""
macOS Setup Script for Orakulum
This script helps set up the environment and check permissions on macOS
"""

import subprocess
import sys
import platform
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    # Try different installation methods for externally managed environments
    methods = [
        # Try with --user flag first
        [sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
        # Try with --break-system-packages as fallback
        [sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"],
        # Try creating a virtual environment
        None  # Will be handled separately
    ]
    
    for i, method in enumerate(methods):
        if method is None:
            # Create virtual environment as last resort
            print("🔧 Creating virtual environment...")
            try:
                subprocess.check_call([sys.executable, "-m", "venv", "venv"])
                print("✅ Virtual environment created")
                print("📝 To activate the virtual environment, run:")
                print("   source venv/bin/activate")
                print("   pip install -r requirements.txt")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create virtual environment: {e}")
                return False
        else:
            try:
                subprocess.check_call(method)
                print("✅ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                if i < len(methods) - 2:  # Not the last method
                    print(f"⚠️  Method {i+1} failed, trying next...")
                    continue
                else:
                    print(f"❌ Failed to install dependencies: {e}")
                    return False

def check_accessibility_permissions():
    """Check and guide user through accessibility permissions"""
    print("\n🔐 Checking macOS Accessibility Permissions...")
    print("For pyautogui to work, you need to grant accessibility permissions.")
    print("\nTo enable permissions:")
    print("1. Go to System Preferences > Security & Privacy > Privacy")
    print("2. Select 'Accessibility' from the left sidebar")
    print("3. Click the lock icon and enter your password")
    print("4. Add Terminal (or your Python app) to the list")
    print("5. Make sure the checkbox is checked")
    
    input("\nPress Enter after you've enabled accessibility permissions...")
    
    # Test permissions
    try:
        import pyautogui
        pyautogui.moveTo(100, 100, duration=0.1)
        print("✅ Accessibility permissions are working!")
        return True
    except Exception as e:
        print(f"❌ Accessibility permissions not working: {e}")
        return False

def check_playwright():
    """Install Playwright browsers if needed"""
    print("\n🎭 Setting up Playwright...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("✅ Playwright browsers installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        return False

def main():
    print("🚀 Orakulum macOS Setup")
    print("=" * 40)
    
    if platform.system() != "Darwin":
        print("❌ This script is designed for macOS only")
        sys.exit(1)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check accessibility permissions
    if not check_accessibility_permissions():
        print("⚠️  You can still run the script, but automation features may not work")
    
    # Setup Playwright
    if not check_playwright():
        print("⚠️  Playwright setup failed, but you can try running the script anyway")
    
    print("\n✅ Setup complete!")
    print("You can now run: python main.py")

if __name__ == "__main__":
    main()
