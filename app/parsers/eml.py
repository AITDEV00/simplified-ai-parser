"""EML (standard email) to Markdown parser using Python's email stdlib."""
import logging
import email
from email import policy
from email.parser import BytesParser

logger = logging.getLogger(__name__)

def parse_eml_to_markdown(file_path: str) -> str:
    """
    Convert a .eml file to Markdown.
    
    Uses Python's built-in email module (RFC 5322 / MIME compliant).
    Extracts headers, body (text/plain preferred), and attachment list.
    """
    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    parts = []
    
    # Headers
    parts.append("# Email Message\n")
    for header in ["From", "To", "Cc", "Subject", "Date"]:
        value = msg.get(header)
        if value:
            parts.append(f"**{header}:** {value}")
    
    parts.append("\n---\n")
    
    # Body extraction
    body = msg.get_body(preferencelist=("plain", "html"))
    if body:
        content = body.get_content()
        content_type = body.get_content_type()
        if content_type == "text/html":
            from app.core.html_utils import strip_html_to_text
            content = strip_html_to_text(content)
        parts.append(content)
    
    # Attachments
    attachments = list(msg.iter_attachments())
    if attachments:
        parts.append("\n## Attachments\n")
        for att in attachments:
            filename = att.get_filename() or "unknown"
            size = len(att.get_content()) if att.get_content() else 0
            parts.append(f"- 📎 {filename} ({size} bytes)")
    
    return "\n".join(parts)
