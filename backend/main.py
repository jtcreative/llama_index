# -*- coding: utf-8 -*-
"""
Entry point for Entertwine Chatbot SDK

This module provides compatibility with the old main.py interface.
For production use, run with: uvicorn main:app --host 0.0.0.0 --port 3978
"""

import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the FastAPI app from the new structure
from app import app

logger.info("Entertwine Chatbot SDK initialized")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Entertwine Chatbot on port 3978")
    uvicorn.run(app, host="0.0.0.0", port=3978)