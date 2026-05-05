import os
import time
import tempfile
import logging
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.api.schemas import ParseResponse
from app.parsers.registry import get_file_type, parse_document, SUPPORTED_EXTENSIONS
from app.core.image_utils import extract_and_replace_images
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/parse-file", response_model=ParseResponse)
async def parse_file(file: UploadFile = File(...)):
    """
    Parse an uploaded file and convert it to Markdown.

    Accepts: .docx, .xlsx, .xls, .xlsm, .pdf, .md, .markdown

    Returns JSON with:
    - filename: Original filename
    - file_type: Detected file type
    - parsed_md_content: Markdown content
    - processing_time: Time taken in seconds
    """
    start_time = time.time()

    # Validate file extension
    try:
        ext, file_type = get_file_type(file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e) + f". Supported types: {', '.join(SUPPORTED_EXTENSIONS.keys())}"
        )

    # Save uploaded file to temp location
    temp_file = None
    try:
        content = await file.read()
        
        # Check file size
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if len(content) > max_size_bytes:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
            )

        # Create temp file with correct extension
        suffix = ext
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(content)
        temp_file.close()

        # Parse the document concurrently
        try:
            markdown_content = await asyncio.to_thread(parse_document, temp_file.name, file_type)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.exception(f"Error parsing file {file.filename}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse file: {str(e)}"
            )

        # Extract images and replace with UUID references concurrently
        modified_content, images = await asyncio.to_thread(extract_and_replace_images, markdown_content)

        processing_time = time.time() - start_time

        return ParseResponse(
            filename=file.filename,
            file_type=file_type,
            parsed_md_content=modified_content,
            processing_time=round(processing_time, 3),
            images=images
        )

    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
