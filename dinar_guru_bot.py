import re
from bs4 import BeautifulSoup


def extract_posts_in_list(content_html=None, soup=None):
    """
    Alternative approach: Use regex on the raw HTML string to split posts.
    More reliable for this specific HTML structure.
    """
    if soup is not None:
        content_html = str(soup)
    elif content_html is None:
        raise ValueError("Either content_html or soup must be provided")

    # Pattern to match post headers: date followed by title in red font
    # Matches: <strong> [optional <br/>] date <font color="#c23b3b">title</font> </strong>
    post_header_pattern = re.compile(
        r"<strong>\s*(?:<br\s*/?>)?\s*(?:<br\s*/?>)?\s*(\d{1,2}-\d{1,2}-\d{4})\s*"
        r'<font\s+color="#c23b3b">\s*(.+?)\s*</font>',
        re.DOTALL | re.IGNORECASE,
    )

    # Find all matches with their positions
    matches = list(post_header_pattern.finditer(content_html))

    posts = []
    for idx, match in enumerate(matches):
        date_text = match.group(1).strip()
        title_text = match.group(2).strip()

        # Content starts after this match 
        content_start = match.end()

        # Content ends at the start of the next post or end of document
        if idx + 1 < len(matches):
            # Find the <br/><br/><strong> before the next post
            next_match = matches[idx + 1]
            content_end = next_match.start()

            # Look for <br/><br/> or similar ending pattern
            content_html_slice = content_html[content_start:content_end]

            # Remove trailing <br/><br/> pattern
            content_html_slice = re.sub(
                r"\s*<br\s*/?>\s*<br\s*/?>\s*$", "", content_html_slice
            )
        else:
            content_html_slice = content_html[content_start:]
            # Remove trailing <br/><br/> and closing tags
            content_html_slice = re.sub(
                r"\s*<br\s*/?>\s*<br\s*/?>\s*</div>\s*$", "", content_html_slice
            )

        # Parse content HTML to get text
        content_soup = BeautifulSoup(content_html_slice, "html.parser")
        content_text = content_soup.get_text()

        # Clean up whitespace
        content_text = re.sub(r"\s+", " ", content_text).strip()

        # Clean up space + [Post <anything>]
        pattern = r" \[Post [^\]]*\]"
        content_text = re.sub(pattern, "", content_text)

        posts.append(
            {
                "no": idx + 1,
                "date": date_text,
                "title": title_text,
                "content": content_text,
            }
        )

    return posts


def extract_posts_soup():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    from bs4 import BeautifulSoup

    options = Options()
    options.page_load_strategy = "eager"  # 'normal', 'eager', 'none'

    options.add_argument("--start-maximized")  # start browser maximized
    options.add_argument("--disable-infobars")  # remove info bars
    options.add_argument("--disable-extensions")  # disable extensions

    # 'eager' waits only for DOMContentLoaded, not full images/scripts
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    driver.get("https://www.dinarguru.com/")

    # Get the full page HTML content
    full_html_content = driver.page_source

    # Parse and prettify
    soup = BeautifulSoup(full_html_content, "html.parser")

    posts_element = soup.select_one(
        "#wsite-content > div:nth-child(5) > div > div > table > tbody > tr > td:nth-child(2) > div:nth-child(4)"
    )

    posts_content_html = str(posts_element)
    posts_content_html = re.sub(
        r"[\u00A0\u200B\u200C\u200D\uFEFF]", " ", posts_content_html
    )

    soup = BeautifulSoup(posts_content_html, "html.parser")

    driver.quit()

    return soup


def run_dinar_guru_bot():
    soup = extract_posts_soup()
    posts = extract_posts_in_list(soup=soup)

    return posts
