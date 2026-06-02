#!/usr/bin/env python3
"""
Convert HTML to PDF using weasyprint or alternative methods
"""

import subprocess
import sys
import os

html_file = "/home/hibta/ROBUST04_Conversation_Summary.html"
pdf_file = "/home/hibta/ROBUST04_Conversation_Summary.pdf"

def try_weasyprint():
    """Try using weasyprint via command line"""
    try:
        result = subprocess.run(
            ['weasyprint', html_file, pdf_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✓ PDF created with weasyprint: {pdf_file}")
            return True
        else:
            print(f"weasyprint failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("weasyprint not found")
        return False
    except Exception as e:
        print(f"weasyprint error: {e}")
        return False

def try_wkhtmltopdf():
    """Try using wkhtmltopdf"""
    try:
        result = subprocess.run(
            ['wkhtmltopdf', '--enable-local-file-access', html_file, pdf_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✓ PDF created with wkhtmltopdf: {pdf_file}")
            return True
        else:
            print(f"wkhtmltopdf failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("wkhtmltopdf not found")
        return False
    except Exception as e:
        print(f"wkhtmltopdf error: {e}")
        return False

def try_chrome_headless():
    """Try using Chrome/Chromium in headless mode"""
    chrome_commands = [
        'google-chrome',
        'chromium-browser',
        'chromium',
        'google-chrome-stable'
    ]

    for chrome_cmd in chrome_commands:
        try:
            result = subprocess.run(
                [chrome_cmd, '--headless', '--disable-gpu',
                 f'--print-to-pdf={pdf_file}',
                 f'file://{html_file}'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and os.path.exists(pdf_file):
                print(f"✓ PDF created with {chrome_cmd}: {pdf_file}")
                return True
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"{chrome_cmd} error: {e}")
            continue

    print("No Chrome/Chromium found")
    return False

def main():
    print("="*70)
    print("Converting HTML to PDF")
    print("="*70)
    print(f"Input:  {html_file}")
    print(f"Output: {pdf_file}")
    print()

    # Try different methods in order of preference
    methods = [
        ("weasyprint", try_weasyprint),
        ("wkhtmltopdf", try_wkhtmltopdf),
        ("Chrome headless", try_chrome_headless),
    ]

    for method_name, method_func in methods:
        print(f"Trying {method_name}...")
        if method_func():
            print(f"\n✓ Success! PDF created at: {pdf_file}")

            # Check file size
            if os.path.exists(pdf_file):
                size = os.path.getsize(pdf_file)
                print(f"  File size: {size:,} bytes ({size/1024:.1f} KB)")
            return 0
        print()

    print("❌ All conversion methods failed.")
    print("\nAlternative: Open the HTML file in your browser and use 'Print to PDF'")
    print(f"HTML file location: {html_file}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
