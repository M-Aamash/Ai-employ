"""
LinkedIn Post - Interactive Helper

Opens LinkedIn, fills content, then shows you exactly what to do.
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

try:
    import pyperclip
except ImportError:
    os.system('pip install pyperclip')
    import pyperclip

CONTENT = """🚀 Exciting news! We're helping businesses automate their operations with AI-powered solutions.

Our AI employees work 24/7 to:
✅ Handle customer inquiries
✅ Process invoices automatically  
✅ Manage communications
✅ Generate business insights

Ready to transform your business? Let's talk!

#AI #Automation #Business #Innovation #DigitalTransformation"""

def main():
    print("\n" + "=" * 70)
    print("   LinkedIn Post - Interactive Helper")
    print("=" * 70 + "\n")
    
    # Copy to clipboard
    pyperclip.copy(CONTENT)
    print("✓ Post content copied to clipboard\n")
    
    # Open LinkedIn
    print("Opening LinkedIn in your browser...")
    webbrowser.open('https://www.linkedin.com/feed')
    
    print("\n" + "=" * 70)
    print("   FOLLOW THESE EXACT STEPS:")
    print("=" * 70)
    print("\n  STEP 1: Wait for LinkedIn to load in your browser")
    print("          (LinkedIn should already be opening)\n")
    print("  STEP 2: Click 'Start a Post' at the top of your feed\n")
    print("  STEP 3: Press Ctrl+V to paste the content\n")
    print("  STEP 4: Wait 3 seconds for LinkedIn to detect the content\n")
    print("  STEP 5: Click the BLUE 'Post' button")
    print("          (It will be in the bottom-right of the popup)\n")
    print("=" * 70)
    
    print("\nPost Content (already copied):")
    print("-" * 70)
    print(CONTENT)
    print("-" * 70)
    
    print("\n")
    print("IMPORTANT: The Post button only becomes clickable (blue)")
    print("           after LinkedIn detects your content.\n")
    print("           Wait 3-5 seconds after pasting before clicking Post.\n")
    
    # Wait for user to complete
    print("=" * 70)
    print("Press ENTER when you have clicked the Post button...")
    print("=" * 70)
    input()
    
    print("\n" + "=" * 70)
    print("   ✓ Your post should now be publishing to LinkedIn!")
    print("=" * 70)
    print("\nView your post:")
    print("  https://www.linkedin.com/feed")
    print("\nOr check your profile Activity section:\n")
    print("  https://www.linkedin.com/in/your-profile/details/recent-activity/\n")

if __name__ == '__main__':
    main()
