import os
import logging
from typing import Tuple

from app.parsers.docx import parse_docx_to_markdown
from app.parsers.xlsx import parse_xlsx_to_markdown
from app.parsers.pdf import parse_pdf_to_markdown
from app.parsers.markdown import parse_markdown
from app.parsers.pptx import parse_pptx_to_markdown
from app.parsers.msg import parse_msg_to_markdown
from app.parsers.eml import parse_eml_to_markdown

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".xls": "xls",
    ".xlsm": "xlsm",
    ".pdf": "pdf",
    ".md": "markdown",
    ".markdown": "markdown",
    ".pptx": "pptx",
    ".ppt": "ppt",
    ".msg": "msg",
    ".eml": "eml",
}

def get_file_type(filename: str) -> Tuple[str, str]:
    """Get file type from filename."""
    _, ext = os.path.splitext(filename.lower())

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    return ext, SUPPORTED_EXTENSIONS[ext]

def parse_document(file_path: str, file_type: str) -> str:
    """Parse a document and convert it to Markdown."""
    logger.info(f"Parsing {file_type} file: {file_path}")

    if file_type == "docx":
        return parse_docx_to_markdown(file_path)
    elif file_type in ("xlsx", "xlsm"):
        return parse_xlsx_to_markdown(file_path)
    elif file_type == "xls":
        try:
            return parse_xlsx_to_markdown(file_path)
        except Exception as e:
            logger.warning(f"Direct XLS parsing failed: {e}")
            raise RuntimeError(
                "XLS format (Excel 97-2003) may require LibreOffice for conversion. "
                "Please convert to XLSX format, or ensure the file is a valid Excel format."
            )
    elif file_type == "pdf":
        return parse_pdf_to_markdown(file_path)
    elif file_type == "markdown":
        return parse_markdown(file_path)
    elif file_type == "pptx":
        return parse_pptx_to_markdown(file_path)
    elif file_type == "ppt":
        try:
            return parse_pptx_to_markdown(file_path)
        except Exception as e:
            logger.warning(f"Direct PPT parsing failed: {e}")
            raise RuntimeError(
                "PPT format (PowerPoint 97-2003) may not be fully supported. "
                "Please convert to PPTX format for best results."
            )
    elif file_type == "msg":
        return parse_msg_to_markdown(file_path)
    elif file_type == "eml":
        return parse_eml_to_markdown(file_path)
    else:
        raise ValueError(f"Unknown file type: {file_type}")
