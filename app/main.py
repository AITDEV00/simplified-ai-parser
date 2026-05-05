import os
import tempfile
from fastapi import FastAPI
from app.api.routes import router as parse_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Simplified AI Parser",
    description="Lightweight document-to-Markdown conversion service",
    version="0.1.0",
)

app.include_router(parse_router, prefix="/v1")


@app.get("/health")
async def health_check():
    health_status = {"status": "healthy", "checks": {}}
    
    # Check if temp directory is writable
    try:
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"test")
        health_status["checks"]["temp_dir"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["temp_dir"] = f"error: {str(e)}"
        
    return health_status
