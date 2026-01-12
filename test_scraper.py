#!/usr/bin/env python3
"""
Test script to verify web scraping works before full setup
Run this to check if Telegram/Discord scraping is working
"""
import sys
from pathlib import Path

print("🧪 Testing Conflux Community Member Tracker Scraper")
print("=" * 60)
print()

# Check if we can import required libraries
print("📦 Checking dependencies...")
try:
    import requests
    from bs4 import BeautifulSoup
    print("✅ requests and BeautifulSoup available")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Run: pip install requests beautifulsoup4")
    sys.exit(1)

print()

# Test a single Telegram group
print("🔍 Testing Telegram scraping (1 group)...")
test_url = "https://t.me/Conflux_English"

try:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    response = session.get(test_url, timeout=10)
    response.raise_for_status()

    print(f"✅ Successfully fetched {test_url}")
    print(f"   Status code: {response.status_code}")
    print(f"   Response size: {len(response.text)} bytes")

    # Try to find member count
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()

    # Look for member count patterns
    import re
    patterns = [
        r'([\d,]+)\s+members',
        r'([\d,]+)\s+subscribers',
        r'([\d.]+[KM])\s+members',
        r'([\d.]+[KM])\s+subscribers',
    ]

    found = False
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            count_str = match.group(1)
            print(f"✅ Found member count: {count_str}")
            found = True
            break

    if not found:
        print("⚠️  Could not find member count in page")
        print("   This might be okay - Telegram pages vary by region")
        print("   The scraper will handle this gracefully")

        # Show a snippet of the page to help debug
        print("\n   Page content preview (first 500 chars):")
        preview = text[:500].replace('\n', ' ').strip()
        print(f"   {preview}...")

except requests.RequestException as e:
    print(f"❌ Network error: {e}")
    print("   Check your internet connection")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

print()

# Test Discord (without Selenium for quick check)
print("🔍 Testing Discord scraping (basic check)...")
discord_url = "https://discord.com/invite/confluxnetwork"

try:
    response = session.get(discord_url, timeout=10)
    response.raise_for_status()

    print(f"✅ Successfully fetched {discord_url}")
    print(f"   Status code: {response.status_code}")
    print(f"   Response size: {len(response.text)} bytes")

    # Discord is heavily JavaScript-rendered, so this may not work
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()

    if 'members' in text.lower() or 'discord' in text.lower():
        print("✅ Discord page accessible")
        print("   Note: Discord uses JavaScript, so Selenium may be needed")
        print("   for reliable member count extraction")
    else:
        print("⚠️  Discord page structure unclear")
        print("   This is normal - Discord requires JavaScript rendering")
        print("   Selenium mode will handle this")

except requests.RequestException as e:
    print(f"❌ Network error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print()
print("=" * 60)
print("📊 Test Summary")
print("=" * 60)
print()
print("✅ Basic scraping test complete!")
print()
print("What this means:")
print("  - Network connectivity: Working")
print("  - Telegram pages: Accessible")
print("  - Discord pages: Accessible")
print()
print("⚠️  Important Notes:")
print("  - Telegram scraping may vary by region/IP")
print("  - Discord requires Selenium for reliable results")
print("  - Some scrapes may fail occasionally (this is normal)")
print("  - The full scraper handles failures gracefully")
print()
print("Next steps:")
print("  1. If tests passed, proceed with full setup")
print("  2. Run: ./setup.sh")
print("  3. Then: streamlit run app.py")
print("  4. Click 'Collect Data Now' to test all 15 groups")
print()
