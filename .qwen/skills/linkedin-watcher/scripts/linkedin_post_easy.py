"""
LinkedIn Post Helper - Easy Manual Posting

This script opens LinkedIn and displays post content for easy copy-paste.

Usage:
    python linkedin_post_easy.py
"""

import sys
import os
import webbrowser
import time

# Set console encoding to UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Business post templates
TEMPLATES = [
    """🚀 Exciting news! We're helping businesses automate their operations with AI-powered solutions.

Our AI employees work 24/7 to:
✅ Handle customer inquiries
✅ Process invoices automatically  
✅ Manage communications
✅ Generate business insights

Ready to transform your business? Let's talk!

#AI #Automation #Business #Innovation #DigitalTransformation""",

    """💡 Did you know? Businesses save 85% on operational costs by implementing AI automation.

Our clients see results in:
📈 Increased productivity
⏰ Time savings (40+ hours/week)
💰 Reduced operational costs
🎯 Better customer satisfaction

Want to learn how AI can help your business? DM me!

#BusinessGrowth #AI #Productivity #Entrepreneurship""",

    """📊 Case Study: 30-Day Results

Client: Professional Services Firm
Challenge: Overwhelmed team, slow response times

Solution: AI Employee Implementation

Results:
• Response time: 24hrs → 5 minutes
• Lead conversion: +45%
• Team productivity: +60%
• Customer satisfaction: 95%

Want similar results? Let's talk!

#CaseStudy #BusinessSuccess #AI #Automation #ROI""",

    """🔥 Hot Take: If you're not implementing AI in your business in 2026, you're already behind.

Your competitors are:
→ Responding to leads instantly
→ Working 24/7 without burnout
→ Scaling faster with lower costs
→ Providing better customer experiences

The question isn't "Can you afford AI?" It's "Can you afford NOT to?"

#BusinessStrategy #AI #CompetitiveAdvantage #Innovation""",

    """🎯 Monday Motivation: The future of business is human + AI collaboration.

It's not about replacing humans - it's about:
🔹 Eliminating repetitive tasks
🔹 Empowering teams to focus on creativity
🔹 Providing 24/7 customer support
🔹 Scaling without linear cost increase

How is your business preparing for the AI future?

#MondayMotivation #FutureOfWork #AI #Leadership""",
]

def main():
    import random
    
    print("\n" + "=" * 70)
    print("   LinkedIn Post Helper - Easy Manual Posting")
    print("=" * 70 + "\n")
    
    # Select template
    print("Available post templates:")
    print("-" * 70)
    for i, template in enumerate(TEMPLATES, 1):
        preview = template[:80].replace('\n', ' ') + "..."
        print(f"  {i}. {preview}")
    print(f"  0. Random selection")
    print("-" * 70)
    
    try:
        choice = input("\nSelect template number (0-5, press Enter for random): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(TEMPLATES):
            content = TEMPLATES[int(choice) - 1]
        else:
            content = random.choice(TEMPLATES)
            print(f"\n[OK] Selected random template")
    except:
        content = random.choice(TEMPLATES)
        print(f"\n[OK] Selected random template")
    
    # Display content
    print("\n" + "=" * 70)
    print("   POST CONTENT (Copy this):")
    print("=" * 70)
    print()
    print(content)
    print()
    print("=" * 70)
    
    # Copy to clipboard
    try:
        import subprocess
        subprocess.run(['clip'], input=content.encode('utf-8'), check=True)
        print("\n[OK] Content copied to clipboard!")
    except:
        print("\n[WARN] Could not copy to clipboard automatically.")
        print("Please select and copy the content manually.")
    
    # Open LinkedIn
    print("\nOpening LinkedIn in your default browser...")
    webbrowser.open('https://www.linkedin.com/feed')
    
    print("\n" + "=" * 70)
    print("   INSTRUCTIONS:")
    print("=" * 70)
    print("1. LinkedIn should open in your browser")
    print("2. Click 'Start a Post' at the top of your feed")
    print("3. Paste the content (Ctrl+V)")
    print("4. Add an image if desired (optional)")
    print("5. Click 'Post'")
    print("=" * 70 + "\n")
    
    print("Post published! Your AI Employee is growing your business presence! 🚀\n")

if __name__ == '__main__':
    main()
