"""Test script to find working Reddit selectors."""
from playwright.sync_api import sync_playwright
import time

test_url = "https://www.reddit.com/r/TeamfightTactics/comments/1b6zdh8/i_hate_this/"

print("🔍 Testing Reddit Selectors\n")
print(f"URL: {test_url}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless=False so you can see it
    page = browser.new_page()

    print("🌐 Loading page...")
    page.goto(test_url, wait_until="networkidle", timeout=60000)

    print("✅ Page loaded!\n")

    # Wait a bit for dynamic content
    time.sleep(3)

    # Test different selectors (from most specific to most generic)
    selectors_to_test = [
        # Old Reddit selectors
        '[data-test-id="post-content"]',

        # New Reddit custom elements
        'shreddit-post',
        'shreddit-post-detail',

        # Slot-based
        '[slot="post-media-container"]',
        '[slot="text-body"]',

        # Data attributes
        '[data-post-click-location="text-body"]',
        '[data-testid="post-container"]',
        '[data-click-id="text"]',

        # HTML5 semantic
        'article',
        'main article',

        # Class-based (less reliable)
        '.Post',
        '[class*="Post"]',
        'div[id*="post"]',

        # Generic fallbacks
        'main [role="main"]',
    ]

    print("Testing selectors:\n")
    working_selectors = []

    for selector in selectors_to_test:
        try:
            elements = page.locator(selector).all()
            if elements:
                print(f"✅ FOUND: {selector} ({len(elements)} element(s))")
                working_selectors.append(selector)

                # Show first element's tag name to verify
                first_el = page.locator(selector).first
                tag_name = first_el.evaluate("el => el.tagName")
                print(f"   └─ Tag: <{tag_name.lower()}>")
            else:
                print(f"❌ NOT FOUND: {selector}")
        except Exception as e:
            print(f"❌ ERROR: {selector} - {str(e)[:50]}")

    print("\n" + "="*60)
    print(f"✅ Found {len(working_selectors)} working selector(s)")
    if working_selectors:
        print(f"🎯 RECOMMENDED: {working_selectors[0]}")
        print("\nAll working selectors:")
        for sel in working_selectors:
            print(f"  - {sel}")

    print("\n" + "="*60)
    print("Press Enter to close browser...")
    input()

    browser.close()

print("\n✅ Test complete!")
