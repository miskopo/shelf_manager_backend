# main.py
import logging
import uvicorn
from pantry.api import create_app

logger = logging.getLogger("pantry")

app = create_app()

if __name__ == "__main__":
    logger.info("Starting Pantry Manager API...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )