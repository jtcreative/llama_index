# -*- coding: utf-8 -*-
"""
FastAPI application factory for Entertwine Chatbot
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ChatbotConfig

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    This factory function validates configuration and sets up the app
    without blocking on heavy initialization.
    
    Returns:
        Configured FastAPI application
        
    Raises:
        ValueError: If configuration is invalid
    """
    try:
        # Validate configuration upfront
        logger.info("Validating configuration...")
        ChatbotConfig.validate()
        
        # Create app
        app = FastAPI(
            title="Entertwine Chatbot API",
            description="Self-hosted chatbot powered by Azure OpenAI",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        from .routes import router
        app.include_router(router)
        
        # Add startup event
        @app.on_event("startup")
        async def startup():
            logger.info("Entertwine Chatbot API starting up")
        
        # Add shutdown event
        @app.on_event("shutdown")
        async def shutdown():
            logger.info("Entertwine Chatbot API shutting down")
        
        logger.info("FastAPI application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


# Create default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3978)
