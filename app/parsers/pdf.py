"""
PDF to Markdown Parser using pymupdf4llm
"""
import logging
import pymupdf4llm

logger = logging.getLogger(__name__)

def parse_pdf_to_markdown(file_path: str) -> str:
    """
    Convert a PDF file to Markdown format using pymupdf4llm.
    
    This library natively extracts tables, images (if configured),
    and layout structures to high-fidelity markdown without relying on mutool.
    """
    logger.info(f"Parsing PDF using pymupdf4llm: {file_path}")
    
    try:
        # We don't use write_images=True here because our image extraction
        # pipeline currently relies on base64 encoded images inline.
        # pymupdf4llm by default will output text, lists, and tables.
        # If image extraction directly from PDF is needed later, 
        # it can be configured here.
        markdown_content = pymupdf4llm.to_markdown(file_path)
        
        # Clean up whitespace
        from app.core.markdown_utils import clean_whitespace
        return clean_whitespace(markdown_content)
        
    except Exception as e:
        logger.error(f"pymupdf4llm conversion failed: {e}")
        raise RuntimeError(f"Failed to convert PDF: {str(e)}")
