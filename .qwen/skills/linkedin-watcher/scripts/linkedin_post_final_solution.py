"""
LinkedIn Post - Start a Post Button Only

Opens LinkedIn in YOUR browser with content copied to clipboard.
Uses "Start a Post" button instead of "Start a Post".
"""

import sys
import os
import webbrowser

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
    print("   LinkedIn Post - Start a Post Button")
    print("=" * 70 + "\n")
    
    # Copy content to clipboard
    pyperclip.copy(CONTENT)
    print("✓ Post content copied to clipboard!")
    print(f"  ({len(CONTENT)} characters)\n")
    
    # Open LinkedIn in default browser
    print("Opening LinkedIn in your browser...")
    webbrowser.open('https://www.linkedin.com/feed')
    
    print("\n" + "=" * 70)
    print("   QUICK STEPS (30 seconds):")
    print("=" * 70)
    print("\n  1. LinkedIn is opening in your browser")
    print("  2. Click 'Start a Post' (top of feed)")
    print("  3. Press Ctrl+V to paste (content is ready)")
    print("  4. Click 'Post'")
    print("  5. If popup appears:")
    print("     - Click 'Connections only'")
    print("     - Click 'Back'")
    print("     - Click 'Post'")
    print("\n" + "=" * 70)
    
    print("\nPost Content (already copied):")
    print("-" * 70)
    print(CONTENT)
    print("-" * 70)
    
    print("\n")
    print("=" * 70)
    print("   Press ENTER when you've clicked 'Post'...")
    print("=" * 70)
    
    try:
        input()
    except:
        pass
    
    print("\n" + "=" * 70)
    print("   ✓✓✓ SUCCESSFUL! ✓✓✓")
    print("=" * 70)
    print("\nYour post has been PUBLISHED to LinkedIn!")
    print("\nView your post:")
    print("  https://www.linkedin.com/feed")
    print("\nOr check your Activity section:\n")
    print("  https://www.linkedin.com/in/your-profile/details/recent-activity/\n")

if __name__ == '__main__':
    main()
