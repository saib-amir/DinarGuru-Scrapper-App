"""
Dinar Recaps Bot

A web scraping bot that extracts blog post metadata and content from dinarrecaps.com.
Uses Selenium WebDriver for browser automation and BeautifulSoup for HTML parsing.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def create_driver():
    """
    Create and configure a Selenium Chrome WebDriver instance.

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance.
    """
    options = Options()
    options.page_load_strategy = "eager"  # Wait for DOMContentLoaded, not full load
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    return driver


def extract_posts_metadata(driver):
    """
    Extract metadata (title, date, link) from all blog posts on the main page.

    Args:
        driver: Selenium WebDriver instance.

    Returns:
        list: List of dictionaries containing post metadata.
              Each dict has keys: 'no', 'date', 'title', 'link'
    """
    driver.get("https://dinarrecaps.com/our-blog")

    # Wait for post elements to load
    post_elements = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (
                By.CSS_SELECTOR,
                "article.blog-single-column--container.entry.blog-item.no-image-fade-in",
            )
        )
    )

    # Extract data from each post element
    posts = []
    for index, post in enumerate(post_elements, start=1):
        title = post.find_element(By.CSS_SELECTOR, ".blog-title").text
        link = post.find_element(By.CSS_SELECTOR, ".blog-title a").get_attribute("href")
        date = post.find_element(By.CSS_SELECTOR, ".blog-date").text

        posts.append({"no": index, "date": date, "title": title, "link": link})

    return posts


def add_html_content_to_posts(posts, driver, date=None):
    """
    Add HTML content to each post by visiting its link.

    Args:
        posts: List of post dictionaries with keys: no, date, title, link
        driver: Selenium WebDriver instance.
        date: Optional date string to filter posts. If provided, only posts
              matching this date will be processed.

    Returns:
        list: Updated posts list with 'content' key added to processed posts.
    """
    for post in posts:
        # Skip posts that don't match the date filter (if provided)
        if date is not None and post["date"] != date:
            continue

        # Load the post page
        driver.get(post["link"])

        # Get page source and parse with BeautifulSoup
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # Select all matching HTML blocks
        blocks = soup.select(".sqs-block.html-block.sqs-block-html")

        # Merge inner HTML of all blocks except the last one
        merged_html = ""
        if len(blocks) > 1:
            for block in blocks[:-1]:
                merged_html += block.decode_contents()
        elif len(blocks) == 1:
            # If only one block exists, use it (no exclusion needed)
            merged_html = blocks[0].decode_contents()

        # Add content to the post dictionary (remove newlines)
        post["content"] = merged_html.replace("\n", "")

    return posts


def run_dinar_recaps_bot(date=None):
    """
    Main function to run the Dinar Recaps scraping bot.

    Extracts post metadata from the blog, then fetches full HTML content
    for each post (optionally filtered by date).

    Args:
        date: Optional date string to filter posts (e.g., "12/4/25").
              If None, all posts are processed.

    Returns:
        list: List of post dictionaries with metadata and content.
    """
    # Create a single driver instance for all operations
    driver = create_driver()

    try:
        # Extract metadata from all posts on the main page
        posts = extract_posts_metadata(driver)
        print(f"Found {len(posts)} posts")

        for post in posts:
            print(f"  {post['no']}. [{post['date']}] {post['title']}")

        # Add HTML content to posts (optionally filtered by date)
        posts = add_html_content_to_posts(posts, driver, date=date)

        return posts

    finally:
        # Ensure driver is closed even if an error occurs
        driver.quit()
