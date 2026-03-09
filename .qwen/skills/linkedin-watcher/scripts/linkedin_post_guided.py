"""
LinkedIn Post - Step by Step Guided

This script guides you through posting to LinkedIn step by step.
"""

import sys
import os
import time
import webbrowser
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Post content
CONTENT = """🎯 Monday Motivation: The future of business is human + AI collaboration.

It's not about replacing humans - it's about:
🔹 Eliminating repetitive tasks
🔹 Empowering teams to focus on creativity
🔹 Providing 24/7 customer support
🔹 Scaling without linear cost increase

How is your business preparing for the AI future?

#MondayMotivation #FutureOfWork #AI #Leadership"""

def main():
    print("\n" + "=" * 70)
    print("   LinkedIn Post - Step by Step Guide")
    print("=" * 70 + "\n")
    
    # Copy to clipboard
    try:
        import subprocess
        subprocess.run(['clip'], input=CONTENT.encode('utf-8'), check=True)
        print("[OK] Content copied to clipboard!")
    except:
        print("[WARN] Could not copy automatically. Please select and copy manually.")
    
    # Open LinkedIn
    print("\nOpening LinkedIn...")
    webbrowser.open('https://www.linkedin.com/feed')
    
    print("\n" + "=" * 70)
    print("   FOLLOW THESE STEPS:")
    print("=" * 70)
    print("\nSTEP 1: Wait for LinkedIn to open in your browser")
    print("        (LinkedIn should open automatically)")
    print("\nSTEP 2: Click 'Start a Post' at the top of your feed")
    print("\nSTEP 3: Press Ctrl+V to paste the content")
    print("        (Content is already copied to your clipboard)")
    print("\nSTEP 4: Click the 'Post' button")
    print("\n" + "=" * 70)
    
    print("\nPost Content:")
    print("-" * 70)
    print(CONTENT)
    print("-" * 70)
    
    print("\n")
    
    # Wait for user confirmation
    while True:
        answer = input("Have you clicked 'Post'? (yes/no): ").strip().lower()
        
        if answer in ['yes', 'y']:
            print("\n" + "=" * 70)
            print("   ✓ SUCCESS! Your post is now live on LinkedIn!")
            print("=" * 70)
            print("\nYour AI Employee has successfully posted to LinkedIn! 🚀")
            print("Check your profile to see the published post.\n")
            break
        elif answer in ['no', 'n']:
            print("\nPlease complete the steps above, then type 'yes'.\n")
            print("Reminder:")
            print("  1. Click 'Start a Post'")
            print("  2. Press Ctrl+V to paste")
            print("  3. Click 'Post' button\n")
        else:
            print("Please type 'yes' or 'no'\n")

if __name__ == '__main__':
    main()
