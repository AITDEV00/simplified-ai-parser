"""MSG (Outlook email) to Markdown parser using extract-msg."""
import logging
from typing import Tuple, List

import extract_msg

logger = logging.getLogger(__name__)

def parse_msg_to_markdown(file_path: str) -> str:
    """
    Convert an Outlook .msg file to Markdown.
    
    Extracts:
    - Email headers (From, To, Cc, Subject, Date)
    - Body content (prefers plain text, falls back to stripped HTML)
    - Attachment list
    """
    msg = extract_msg.Message(file_path)
    try:
        parts = []
        
        # Headers
        parts.append("# Email Message\n")
        if msg.sender:
            parts.append(f"**From:** {msg.sender}")
        if msg.to:
            parts.append(f"**To:** {msg.to}")
        if msg.cc:
            parts.append(f"**Cc:** {msg.cc}")
        if msg.subject:
            parts.append(f"**Subject:** {msg.subject}")
        if msg.date:
            parts.append(f"**Date:** {msg.date}")
        
        parts.append("\n---\n")
        
        # Body
        if msg.body and msg.body.strip():
            parts.append(msg.body)
        elif msg.htmlBody:
            # Strip HTML to plain text as fallback
            from app.core.html_utils import strip_html_to_text
            parts.append(strip_html_to_text(msg.htmlBody))
        
        # Attachments
        if msg.attachments:
            parts.append("\n## Attachments\n")
            for att in msg.attachments:
                name = getattr(att, 'longFilename', None) or getattr(att, 'shortFilename', 'unknown')
                size = getattr(att, 'dataLength', None) or 0
                parts.append(f"- 📎 {name} ({size} bytes)")
        
        return "\n".join(parts)
    finally:
        msg.close()
