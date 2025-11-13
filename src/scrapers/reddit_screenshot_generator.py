"""Generate screenshots of Reddit posts using Playwright."""
import os
import time
from pathlib import Path
from typing import Optional, Dict, List
from functools import wraps
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
    """Decorator to retry function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        print(f"❌ Failed after {max_retries} attempts: {e}")
                        raise

                    print(f"⚠️  Attempt {retries} failed: {e}")
                    print(f"   Retrying in {current_delay:.1f}s...")
                    time.sleep(current_delay)
                    current_delay *= 2  # Exponential backoff

        return wrapper
    return decorator


class RedditScreenshotGenerator:
    """Generate styled screenshots of Reddit posts."""

    def __init__(
        self,
        theme: str = "dark",  # dark, light, or transparent
        width: int = 1080,
        height: int = 1920,
        device_scale_factor: float = 2.0
    ):
        """Initialize screenshot generator.

        Args:
            theme: Reddit theme (dark/light/transparent)
            width: Screenshot width
            height: Screenshot height
            device_scale_factor: Pixel density multiplier
        """
        self.theme = theme
        self.width = width
        self.height = height
        self.device_scale_factor = device_scale_factor

    @retry_on_failure(max_retries=3, delay=2.0)
    def capture_post_screenshot(
        self,
        post_url: str,
        output_dir: str = "output/screenshots",
        post_id: str = None,
        capture_comments: bool = False,
        max_comments: int = 5,
        use_cache: bool = True,
        timeout: int = 30000,
        custom_css: str = None,
        font_scale: float = 1.0,
        highlight_color: str = None
    ) -> Dict[str, any]:
        """Capture screenshot of Reddit post and optionally comments.

        Args:
            post_url: Full URL to Reddit post
            output_dir: Directory to save screenshots
            post_id: Reddit post ID (for filename)
            capture_comments: Whether to capture individual comments
            max_comments: Max number of comment screenshots
            use_cache: Whether to reuse cached screenshots
            timeout: Page load timeout in milliseconds (default: 30000)
            custom_css: Custom CSS to inject into page
            font_scale: Font size multiplier (default: 1.0)
            highlight_color: Color for highlighting important text (e.g., "#ffff00")

        Returns:
            Dict with screenshot paths and metadata
        """
        print(f"📸 Capturing screenshot of: {post_url}")

        # Create output directory
        output_path = Path(output_dir)
        if post_id:
            output_path = output_path / post_id
        output_path.mkdir(parents=True, exist_ok=True)

        # Check cache first
        post_screenshot_path = output_path / "post.png"
        if use_cache and post_screenshot_path.exists():
            print(f"♻️  Using cached screenshot: {post_screenshot_path.name}")
            screenshots = {
                "post": str(post_screenshot_path),
                "comments": [],
                "post_url": post_url,
                "cached": True
            }

            # Check for cached comments too
            if capture_comments:
                for i in range(max_comments):
                    comment_path = output_path / f"comment_{i+1}.png"
                    if comment_path.exists():
                        screenshots["comments"].append(str(comment_path))
                    else:
                        break

                if screenshots["comments"]:
                    print(f"♻️  Found {len(screenshots['comments'])} cached comment(s)")

            return screenshots

        screenshots = {
            "post": None,
            "comments": [],
            "post_url": post_url,
            "cached": False
        }

        with sync_playwright() as p:
            # Launch browser (headless for automation)
            browser = p.chromium.launch(headless=True)

            # Create context with theme
            context = browser.new_context(
                viewport={
                    "width": self.width,
                    "height": self.height
                },
                device_scale_factor=self.device_scale_factor,
                color_scheme=self.theme if self.theme in ["dark", "light"] else "dark"
            )

            page = context.new_page()

            try:
                # Navigate to post
                print("🌐 Loading Reddit post...")
                page.goto(post_url, wait_until="networkidle", timeout=timeout)

                # Wait for page to fully stabilize (like RedditVideoMakerBot does)
                page.wait_for_load_state()
                page.wait_for_timeout(2000)  # Extra 2s for dynamic content

                # Apply transparent background if requested
                if self.theme == "transparent":
                    # Inject CSS to make Reddit background transparent
                    page.add_style_tag(content="""
                        /* Make backgrounds transparent */
                        body, [data-test-id="post-content"],
                        [class*="Post"], [class*="post"],
                        [class*="Comment"], [class*="comment"],
                        div[style*="background"] {
                            background: transparent !important;
                            background-color: transparent !important;
                        }

                        /* Keep text readable on transparent bg */
                        [class*="md"], p, span, h1, h2, h3 {
                            text-shadow: 0px 0px 4px rgba(0,0,0,0.8);
                        }
                    """)
                    print("🎨 Applied transparent theme")

                # Apply font scaling if requested
                if font_scale != 1.0:
                    page.add_style_tag(content=f"""
                        /* Scale font sizes */
                        * {{
                            font-size: calc(1em * {font_scale}) !important;
                        }}
                    """)
                    print(f"🔤 Applied font scale: {font_scale}x")

                # Apply text highlighting if requested
                if highlight_color:
                    page.add_style_tag(content=f"""
                        /* Highlight important text */
                        [data-test-id="post-content"] h1,
                        [data-test-id="post-content"] h2,
                        [data-test-id="post-content"] strong,
                        [data-testid="comment"] strong {{
                            background-color: {highlight_color} !important;
                            padding: 2px 4px;
                            border-radius: 3px;
                        }}
                    """)
                    print(f"✨ Applied highlight color: {highlight_color}")

                # Apply custom CSS if provided
                if custom_css:
                    page.add_style_tag(content=custom_css)
                    print("🎨 Applied custom CSS")

                # Handle NSFW warnings
                try:
                    nsfw_button = page.locator('button:has-text("Yes")')
                    if nsfw_button.is_visible(timeout=2000):
                        nsfw_button.click()
                        page.wait_for_load_state("networkidle")
                except:
                    pass  # No NSFW warning

                # Close any popups/overlays
                try:
                    # Close "Use App" prompts
                    close_buttons = page.locator('button[aria-label="Close"]')
                    for i in range(close_buttons.count()):
                        try:
                            close_buttons.nth(i).click(timeout=1000)
                        except:
                            pass
                except:
                    pass

                # Wait for post content to load (try modern selector first, then fallback)
                print("🔍 Finding post element...")
                post_selector = None
                selectors_to_try = [
                    'shreddit-post',           # Modern Reddit custom element
                    'shreddit-post-detail',    # Detailed post view
                    'article',                 # HTML5 semantic
                    '[data-test-id="post-content"]',  # Legacy selector
                ]

                for selector in selectors_to_try:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        if page.locator(selector).count() > 0:
                            post_selector = selector
                            print(f"✅ Found post using selector: {selector}")
                            break
                    except:
                        continue

                if not post_selector:
                    raise Exception("Could not find post element with any known selector")

                # Capture main post screenshot
                print("📷 Capturing post screenshot...")
                post_screenshot_path = output_path / "post.png"

                # Get the post content element
                post_element = page.locator(post_selector).first
                post_element.screenshot(path=str(post_screenshot_path))

                screenshots["post"] = str(post_screenshot_path)
                print(f"✅ Post screenshot saved: {post_screenshot_path.name}")

                # Capture comments if requested
                if capture_comments:
                    print(f"📷 Capturing up to {max_comments} comment screenshots...")

                    # Try modern selectors first, then fallback
                    comment_selector = None
                    comment_selectors_to_try = [
                        'shreddit-comment',        # Modern Reddit custom element
                        '[data-testid="comment"]', # Legacy selector
                        '[slot="comment"]',        # Slot-based
                    ]

                    for selector in comment_selectors_to_try:
                        if page.locator(selector).count() > 0:
                            comment_selector = selector
                            print(f"🔍 Using comment selector: {selector}")
                            break

                    if not comment_selector:
                        print("⚠️  No comments found with any known selector")
                    else:
                        comment_elements = page.locator(comment_selector).all()

                        for idx, comment in enumerate(comment_elements[:max_comments]):
                            try:
                                comment_path = output_path / f"comment_{idx+1}.png"
                                comment.screenshot(path=str(comment_path))
                                screenshots["comments"].append(str(comment_path))
                                print(f"✅ Comment {idx+1} screenshot saved")
                            except Exception as e:
                                print(f"⚠️  Failed to capture comment {idx+1}: {e}")
                                continue

                    print(f"✅ Captured {len(screenshots['comments'])} comment screenshots")

            except PlaywrightTimeout as e:
                print(f"❌ Timeout loading Reddit post: {e}")
                raise
            except Exception as e:
                print(f"❌ Error capturing screenshot: {e}")
                raise
            finally:
                # Cleanup
                context.close()
                browser.close()

        return screenshots

    @retry_on_failure(max_retries=3, delay=2.0)
    def capture_simple_screenshot(
        self,
        post_url: str,
        output_path: str,
        scroll_down: int = 0,
        use_cache: bool = True,
        timeout: int = 30000
    ) -> str:
        """Capture a simple full-page screenshot.

        Args:
            post_url: Reddit post URL
            output_path: Where to save screenshot
            scroll_down: Pixels to scroll down before capturing
            use_cache: Whether to reuse cached screenshot
            timeout: Page load timeout in milliseconds (default: 30000)

        Returns:
            Path to screenshot
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Check cache first
        if use_cache and output_path.exists():
            print(f"♻️  Using cached screenshot: {output_path.name}")
            return str(output_path)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": self.width, "height": self.height},
                device_scale_factor=self.device_scale_factor,
                color_scheme=self.theme if self.theme in ["dark", "light"] else "dark"
            )
            page = context.new_page()

            try:
                page.goto(post_url, wait_until="networkidle", timeout=timeout)

                # Wait for page to fully stabilize
                page.wait_for_load_state()
                page.wait_for_timeout(2000)

                # Apply transparent background if requested
                if self.theme == "transparent":
                    page.add_style_tag(content="""
                        /* Make backgrounds transparent */
                        body, [data-test-id="post-content"],
                        [class*="Post"], [class*="post"],
                        [class*="Comment"], [class*="comment"],
                        div[style*="background"] {
                            background: transparent !important;
                            background-color: transparent !important;
                        }

                        /* Keep text readable on transparent bg */
                        [class*="md"], p, span, h1, h2, h3 {
                            text-shadow: 0px 0px 4px rgba(0,0,0,0.8);
                        }
                    """)

                # Handle NSFW and popups
                try:
                    nsfw_button = page.locator('button:has-text("Yes")')
                    if nsfw_button.is_visible(timeout=2000):
                        nsfw_button.click()
                        page.wait_for_load_state("networkidle")
                except:
                    pass

                # Scroll if requested
                if scroll_down > 0:
                    page.evaluate(f"window.scrollBy(0, {scroll_down})")
                    page.wait_for_timeout(1000)

                # Capture screenshot
                page.screenshot(path=str(output_path), full_page=False)
                print(f"✅ Screenshot saved: {output_path}")

                return str(output_path)

            finally:
                context.close()
                browser.close()


# CLI testing
if __name__ == "__main__":
    import sys

    print("📸 Reddit Screenshot Generator Test\n")

    # Test with a known Reddit post
    test_url = "https://www.reddit.com/r/TeamfightTactics/comments/1b6zdh8/i_hate_this/"

    generator = RedditScreenshotGenerator(theme="dark")

    try:
        result = generator.capture_post_screenshot(
            post_url=test_url,
            output_dir="output/screenshots/test",
            post_id="test_post",
            capture_comments=True,
            max_comments=3
        )

        print("\n" + "=" * 60)
        print("✅ SCREENSHOT TEST COMPLETE")
        print("=" * 60)
        print(f"📁 Post screenshot: {result['post']}")
        print(f"📁 Comment screenshots: {len(result['comments'])}")
        for i, comment in enumerate(result['comments'], 1):
            print(f"   {i}. {Path(comment).name}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
