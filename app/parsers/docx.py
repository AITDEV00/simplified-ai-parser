"""
DOCX to Markdown Parser

Uses mammoth to convert DOCX to HTML, then markdownify to convert to Markdown.
This matches the original ai-parser DOCX conversion flow.
"""

import base64
import re
import mammoth
from bs4 import BeautifulSoup
from markdownify import markdownify


SUPPORTED_IMAGE_FORMATS = ["png", "jpg", "jpeg"]
EMBEDDED_OBJECT_SRC = "embedded_object_src"
EMBEDDED_OBJECT_ICON = "📎"


def _convert_image(image):
    """
    Convert embedded image to base64 data URI.
    Matches original behavior from document_parser.py:1378-1383
    """
    # EMF/WMF are embedded objects, not actual images - mark them for replacement
    if image.content_type in ["image/x-emf", "image/x-wmf"]:
        return {"src": EMBEDDED_OBJECT_SRC}

    with image.open() as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")
    return {"src": f"data:{image.content_type};base64,{image_data}"}


def _replace_embedded_object_with_icon(html_content: str) -> str:
    """
    Replace embedded object placeholders with icon.
    Matches original document_parser.py:1375-1376
    """
    pattern = re.compile(rf'<img[^>]*{EMBEDDED_OBJECT_SRC}[^>]*>')
    return pattern.sub(EMBEDDED_OBJECT_ICON, html_content)


from app.core.html_utils import clean_html, filter_unsupported_images
from app.core.markdown_utils import clean_whitespace





def parse_docx_to_markdown(file_path: str) -> str:
    """
    Convert a DOCX file to Markdown format.

    Processing steps (matching original document_parser.py):
    1. mammoth.convert_to_html with image conversion
    2. Replace embedded objects (EMF/WMF) with 📎 icon
    3. Clean HTML (remove styles, scripts, layout attrs)
    4. Filter unsupported image formats
    5. Convert HTML to Markdown

    Args:
        file_path: Path to the DOCX file

    Returns:
        Markdown content as string
    """
    # Step 1: Convert to HTML (matching original line 1094-1097)
    result = mammoth.convert_to_html(
        file_path,
        convert_image=mammoth.images.img_element(_convert_image)
    )
    html_content = result.value

    # Step 2: Replace embedded object placeholders with icon (matching original line 1099)
    html_content = _replace_embedded_object_with_icon(html_content)

    # Step 3: Clean HTML
    html_content = clean_html(html_content)

    # Step 4: Filter unsupported images
    html_content = filter_unsupported_images(html_content, SUPPORTED_IMAGE_FORMATS)

    # Step 5: Convert HTML to Markdown
    markdown_content = markdownify(
        html_content,
        heading_style="ATX",
        bullets="-",
        strip=["style", "script"]
    )

    return clean_whitespace(markdown_content)
