"""
WordPress Bot - Automates post publishing to WordPress using Selenium.

Uses undetected-chromedriver with persistent Chrome profile for login session persistence.
"""

import undetected_chromedriver as uc
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# WordPress URLs
WP_NEW_POST_URL = "https://investmentindicator.com/wp-admin/post-new.php"
WP_LOGIN_URL = "https://investmentindicator.com/wp-login.php"

# Chrome profile directory
PROFILE_DIR = os.path.expanduser("~/Desktop/DinarGuru/Working/chrome_profile")


def create_driver():
    """
    Create and configure an undetected Chrome WebDriver with persistent profile.

    Returns:
        uc.Chrome: Configured Chrome WebDriver instance.
    """
    import subprocess

    # Kill any existing Chrome processes that might lock the profile
    subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
    time.sleep(1)

    os.makedirs(PROFILE_DIR, exist_ok=True)

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-gpu")

    print("Starting Chrome driver...")
    driver = uc.Chrome(options=options, version_main=142)
    print("Chrome driver started successfully!")
    return driver


def wait_for_login(driver, timeout=300):
    """
    Wait for user to manually login if redirected to login page.

    Args:
        driver: Selenium WebDriver instance.
        timeout: Maximum time to wait for login (default 5 minutes).
    """
    current_url = driver.current_url

    if WP_LOGIN_URL in current_url or "wp-login" in current_url:
        print("\n" + "=" * 60)
        print("LOGIN REQUIRED")
        print("=" * 60)
        print("Please log in manually in the browser window.")
        print("Check 'Remember Me' for persistent login.")
        print(f"Waiting up to {timeout // 60} minutes...")
        print("=" * 60 + "\n")

        # Wait until URL changes away from login page
        WebDriverWait(driver, timeout).until(
            lambda d: "wp-login" not in d.current_url
        )
        print("Login successful! Continuing...\n")

        # Small delay to let page fully load after login
        time.sleep(2)


def wait_for_new_post_page(driver, timeout=30):
    """
    Wait for the 'Add New Post' page to fully load.

    Args:
        driver: Selenium WebDriver instance.
        timeout: Maximum time to wait.
    """
    # Wait for the title input to be present (indicates page is loaded)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#title"))
    )


def enter_title(driver, title: str, timeout=20):
    """
    Enter the post title.

    Args:
        driver: Selenium WebDriver instance.
        title: Post title to enter.
        timeout: Maximum time to wait for element.
    """
    title_input = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#title"))
    )
    title_input.clear()
    title_input.send_keys(title)


def enter_content(driver, content: str, timeout=20):
    """
    Enter post content into the TinyMCE editor.

    Args:
        driver: Selenium WebDriver instance.
        content: Post content to enter.
        timeout: Maximum time to wait for elements.
    """
    # Wait for TinyMCE iframe to load
    iframe = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#content_ifr"))
    )

    # Switch to iframe
    driver.switch_to.frame(iframe)

    # Find the body and enter content
    body = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body#tinymce"))
    )
    body.click()
    body.send_keys(content)

    # Switch back to main document
    driver.switch_to.default_content()


def click_publish(driver, timeout=20):
    """
    Click the Publish button.

    Args:
        driver: Selenium WebDriver instance.
        timeout: Maximum time to wait for element.
    """
    time.sleep(5)
    publish_button = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#publish"))
    )
    publish_button.click()


def wait_for_publish_complete(driver, timeout=60):
    """
    Wait for post to be published (URL changes or success message appears).

    Args:
        driver: Selenium WebDriver instance.
        timeout: Maximum time to wait for publish to complete.
    """
    # Wait for URL to change to indicate post is published
    # Published posts have URLs like: /wp-admin/post.php?post=123&action=edit
    # Or the post message "Post published" appears (message=6)
    WebDriverWait(driver, timeout).until(
        lambda d: "post.php?post=" in d.current_url or
                  "message=6" in d.current_url or
                  len(d.find_elements(By.CSS_SELECTOR, "#message.updated")) > 0
    )


def publish_single_post(driver, post: dict):
    """
    Publish a single post to WordPress.

    Args:
        driver: Selenium WebDriver instance.
        post: Dictionary with 'title' and 'content' keys.
    """
    title = post.get("title", "Untitled")
    content = post.get("content", "")
    post_no = post.get("no", "?")

    print(f"  Publishing post #{post_no}: {title}")

    # Enter title
    enter_title(driver, title)

    # Enter content
    enter_content(driver, content)

    # Click publish
    click_publish(driver)

    # Wait for publish to complete
    wait_for_publish_complete(driver)

    print(f"  Post #{post_no} published successfully!")


def publish_posts(posts: list):
    """
    Publish multiple posts to WordPress.

    Args:
        posts: List of dictionaries, each containing:
            - no: Post number (optional)
            - date: Post date (optional)
            - title: Post title
            - content: Post content

    Returns:
        int: Number of posts successfully published.
    """
    if not posts:
        print("No posts to publish.")
        return 0

    print(f"\nStarting WordPress publishing bot...")
    print(f"Posts to publish: {len(posts)}\n")

    driver = create_driver()
    published_count = 0

    try:
        for idx, post in enumerate(posts):
            print(f"\n[{idx + 1}/{len(posts)}] Processing post...")

            # Navigate to Add New Post page
            driver.get(WP_NEW_POST_URL)

            # Check if login is required
            wait_for_login(driver)

            # If redirected after login, navigate back to new post page
            if "post-new.php" not in driver.current_url:
                driver.get(WP_NEW_POST_URL)

            # Wait for page to load
            wait_for_new_post_page(driver)

            # Publish the post
            try:
                publish_single_post(driver, post)
                published_count += 1
            except TimeoutException as e:
                print(f"  Failed to publish post #{post.get('no', idx + 1)}: Timeout")
                print(f"    Error: {e}")
                continue
            except Exception as e:
                print(f"  Failed to publish post #{post.get('no', idx + 1)}: {e}")
                continue

        print("\n" + "=" * 60)
        print(f"PUBLISHING COMPLETE")
        print(f"Successfully published: {published_count}/{len(posts)} posts")
        print("=" * 60 + "\n")

    finally:
        # Keep browser open for user to verify
        print("Browser will remain open. Close it manually when done.")

    return published_count


def run_wordpress_bot(posts: list):
    """
    Main entry point for the WordPress bot.

    Args:
        posts: List of post dictionaries to publish.

    Returns:
        int: Number of posts successfully published.
    """
    return publish_posts(posts)
