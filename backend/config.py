# -*- coding: utf-8 -*-
"""
Configuration management for Entertwine Chatbot SDK
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ChatbotConfig:
    """Configuration for Entertwine Chatbot with validation"""

    def __init__(self):
        """Initialize and validate configuration"""
        self.validate()

    @staticmethod
    def validate() -> None:
        """Validate all required environment variables"""
        required_vars = {
            "REDIS_URL": "Redis connection URL",
            "AZURE_SEARCH_ENDPOINT": "Azure Search endpoint",
            "AZURE_SEARCH_KEY": "Azure Search key",
            "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
            "AZURE_TEXT_TRANSLATION_APIKEY": "Azure Translation API key",
            "AZURE_TEXT_TRANSLATION_REGION": "Azure Translation region",
        }

        missing = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing.append(f"{var} ({description})")

        if missing:
            error_msg = f"Missing required environment variables:\n" + "\n".join(f"  - {v}" for v in missing)
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Configuration validated successfully")

    @staticmethod
    def get_redis_url() -> str:
        """Get Redis URL"""
        return os.getenv("REDIS_URL", "")

    @staticmethod
    def get_azure_search_endpoint() -> str:
        """Get Azure Search endpoint"""
        return os.getenv("AZURE_SEARCH_ENDPOINT", "")

    @staticmethod
    def get_azure_search_key() -> str:
        """Get Azure Search key"""
        return os.getenv("AZURE_SEARCH_KEY", "")

    @staticmethod
    def get_azure_search_index() -> str:
        """Get Azure Search index name"""
        return os.getenv("AZURE_SEARCH_INDEX", "medichat-index")

    @staticmethod
    def get_azure_openai_endpoint() -> str:
        """Get Azure OpenAI endpoint"""
        return os.getenv("ENDPOINT_URL", "https://medichatbot-openai-eastus2.openai.azure.com")

    @staticmethod
    def get_azure_openai_deployment() -> str:
        """Get Azure OpenAI deployment name"""
        return os.getenv("DEPLOYMENT_NAME", "medichat-gpt-35-turbo")

    @staticmethod
    def get_azure_openai_key() -> str:
        """Get Azure OpenAI API key"""
        return os.getenv("AZURE_OPENAI_API_KEY", "")

    @staticmethod
    def get_teams_app_id() -> Optional[str]:
        """Get Microsoft Teams app ID (optional)"""
        return os.getenv("MICROSOFT_APP_ID")

    @staticmethod
    def get_teams_app_password() -> Optional[str]:
        """Get Microsoft Teams app password (optional)"""
        return os.getenv("MICROSOFT_APP_PASSWORD")

    @staticmethod
    def get_teams_tenant_id() -> Optional[str]:
        """Get Microsoft Teams tenant ID (optional)"""
        return os.getenv("MICROSOFT_TENANT_ID")

    @staticmethod
    def get_model_path() -> str:
        """Get language detection model path"""
        return os.path.join(os.path.dirname(__file__), "..", "models", "lid.176.bin")

    @staticmethod
    def get_data_dir() -> str:
        """Get data directory path"""
        return os.path.join(os.path.dirname(__file__), "data")
