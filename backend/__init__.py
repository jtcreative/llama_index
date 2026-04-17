# -*- coding: utf-8 -*-
"""Entertwine Chatbot Backend Package"""

__version__ = "1.0.0"
__author__ = "Entertwine"

# Import config and cli utilities only (no app creation at import time)
try:
    from .config import ChatbotConfig
    from .chat_service import QueryRequest, process_query
except ImportError:
    pass

# Lazy import app only when needed
def get_app():
    """Lazy-load the FastAPI app"""
    from .app import app
    return app

def create_app():
    """Import create_app factory function"""
    from .app import create_app as _create_app
    return _create_app()

__all__ = [
    "create_app",
    "get_app",
    "ChatbotConfig",
    "QueryRequest",
    "process_query",
]
