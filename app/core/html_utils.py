import re
from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """Clean HTML content by removing unnecessary elements."""
    soup = BeautifulSoup(html_content, "html.parser")

    head = soup.head
    if head:
        head.decompose()

    for tag_name in ["style", "script", "video", "audio"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    for element in soup.find_all(style=True):
        del element["style"]

    attrs_to_remove = [
        "align", "valign", "bgcolor", "sdval", "sdnum",
        "height", "width", "cellspacing", "border", "span",
        "hspace", "vspace", "data-sheets-value",
        "data-sheets-numberformat", "data-sheets-formula"
    ]
    for attr in attrs_to_remove:
        for element in soup.find_all(attrs={attr: True}):
            del element[attr]

    for font in soup.find_all("font"):
        font.unwrap()

    for indicator in soup.find_all(class_="comment-indicator"):
        indicator.decompose()

    html_without_comments = re.sub(r"<!--[\s\S]*?-->", "", str(soup))
    return html_without_comments

def filter_unsupported_images(html_content: str, supported_formats: list[str]) -> str:
    """Remove images with unsupported formats from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue

        extension = ""
        if src.startswith("data:image/"):
            matches = re.match(r"^data:image/(\w+);base64", src)
            if matches:
                extension = matches.group(1).lower()

        if extension and extension not in supported_formats:
            img.decompose()

    return str(soup)

def strip_html_to_text(html_content: str) -> str:
    """Strip all HTML tags and return plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)
