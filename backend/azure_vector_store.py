# -*- coding: utf-8 -*-
"""
Azure Vector Store initialization
"""

import logging
from typing import Optional
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from llama_index.core import VectorStoreIndex
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.vector_stores.azureaisearch import AzureAISearchVectorStore
from .chatbot import Settings, client, initialize_settings
from .config import ChatbotConfig

logger = logging.getLogger(__name__)

_query_engine: Optional[RetrieverQueryEngine] = None


def get_query_engine() -> RetrieverQueryEngine:
    """
    Lazy-load and return the query engine.
    
    Returns:
        RetrieverQueryEngine configured with Azure Search
    """
    global _query_engine
    if _query_engine is None:
        _query_engine = initialize_query_engine()
    return _query_engine


def initialize_query_engine() -> RetrieverQueryEngine:
    """
    Initialize query engine with Azure Search vector store.
    
    Returns:
        Configured RetrieverQueryEngine
    """
    try:
        # Ensure Azure OpenAI settings are initialized
        initialize_settings()
        
        logger.info("Initializing Azure Search vector store")
        
        # Get configuration
        endpoint = ChatbotConfig.get_azure_search_endpoint()
        index_name = ChatbotConfig.get_azure_search_index()
        key = ChatbotConfig.get_azure_search_key()
        
        if not all([endpoint, index_name, key]):
            raise ValueError("Azure Search configuration incomplete")
        
        # Initialize search client
        search_client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(key)
        )
        
        logger.info(f"Connected to Azure Search index: {index_name}")
        
        # Create vector store
        azure_vector_store = AzureAISearchVectorStore(
            search_or_index_client=search_client,
            doc_id_field_key="id",
            id_field_key="id",
            chunk_field_key="content",
            embedding_field_key="embedding",
            metadata_string_field_key="metadata_json",
        )
        
        logger.info("Azure Vector Store initialized")
        
        # Create index
        azure_index = VectorStoreIndex.from_vector_store(
            vector_store=azure_vector_store,
            embed_model=Settings.embed_model,
            llm=client
        )
        
        logger.info("Vector index created")
        
        # Create retriever and response synthesizer
        azure_retriever = VectorIndexRetriever(index=azure_index)
        response_synthesizer = get_response_synthesizer(response_mode="refine")
        
        # Create query engine
        query_engine = RetrieverQueryEngine(
            retriever=azure_retriever,
            response_synthesizer=response_synthesizer
        )
        
        logger.info("Query engine initialized successfully")
        return query_engine
        
    except Exception as e:
        logger.error(f"Failed to initialize query engine: {e}")
        raise
