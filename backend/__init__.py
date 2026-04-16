# -*- coding: utf-8 -*-
"""Entertwine Chatbot Backend Package"""

__version__ = "1.0.0"
__author__ = "Entertwine"

# Import main components for easy access
try:
    from .config import ChatbotConfig
    from .chat_service import QueryRequest, process_query
    from .app import app, create_app
except ImportError:
    pass

__all__ = [
    "app",
    "create_app",
    "ChatbotConfig",
    "QueryRequest",
    "process_query",
]
