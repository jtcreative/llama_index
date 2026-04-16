# -*- coding: utf-8 -*-
"""
Chat service business logic
"""

import logging
import redis
from typing import Optional
from pydantic import BaseModel
from .redisMemory import RedisChatMemory
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from .prompt_templates import few_shot_prompt
from .chatbot import client
from .azure_vector_store import get_query_engine
from .language_utils import detect_language, translate_text
from .config import ChatbotConfig

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None

STATE_NAME_TO_CODE = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA", "colorado": "CO",
    "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY"
}


class QueryRequest(BaseModel):
    session_id: str
    query: str


def get_redis_client() -> redis.Redis:
    """
    Lazy-load Redis client.
    
    Returns:
        Redis client
    """
    global _redis_client
    if _redis_client is None:
        try:
            redis_url = ChatbotConfig.get_redis_url()
            logger.info("Connecting to Redis")
            _redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    return _redis_client


def apply_guardrails(response_text: str) -> str:
    """
    Apply safety guardrails to response.
    
    Args:
        response_text: Original response text
        
    Returns:
        Response with guardrails applied
    """
    fallback = "\n\nTo help you better, please provide more specific details like your location or the kind of help you need."
    danger_phrases = ["can you clarify", "not sure", "please rephrase", "need more information"]
    too_short = len(response_text.strip()) < 20

    if any(phrase in response_text.lower() for phrase in danger_phrases) or too_short:
        return response_text.strip() + fallback
    
    return response_text.strip()


async def process_query(request: QueryRequest) -> str:
    """
    Process a chat query.
    
    Args:
        request: QueryRequest with session_id and query
        
    Returns:
        Response text in user's language
    """
    try:
        session_id = request.session_id
        logger.info(f"Processing query for session {session_id}")
        
        # Step 1: Detect language
        clean_query = request.query.strip().lower()
        language, confidence = detect_language(clean_query)
        
        if confidence < 0.2:
            return "Can you rephrase that? I couldn't confidently detect the language."
        
        logger.debug(f"Detected language: {language} (confidence: {confidence})")
        
        # Step 2: Translate to English if needed
        if language != 'en':
            translated_question = translate_text(request.query, 'en', language)
        else:
            translated_question = request.query
        
        # Step 3: Load or create chat memory
        redis_client = get_redis_client()
        memory_key = f"chat:{session_id}"
        memory = RedisChatMemory(redis_client=redis_client, key=memory_key)
        
        # Step 4: Get query engine
        query_engine = get_query_engine()
        
        # Step 5: Create chat engine with memory
        chat_engine = CondenseQuestionChatEngine.from_defaults(
            query_engine=query_engine,
            lm=client,
            memory=memory,
            chat_prompt=few_shot_prompt
        )
        
        # Step 6: Query the chatbot
        logger.debug(f"Querying: {translated_question}")
        answer_in_english = chat_engine.chat(translated_question)
        answer_text = apply_guardrails(answer_in_english.response)
        
        # Step 7: Store in memory
        memory.append("user", translated_question)
        memory.append("assistant", answer_text)
        redis_client.expire(memory_key, 1800)  # 30 min TTL
        
        # Step 8: Translate back to original language
        if language != 'en':
            answer_in_user_language = translate_text(answer_text, language, 'en')
        else:
            answer_in_user_language = answer_text
        
        logger.info(f"Query processed successfully for session {session_id}")
        return answer_in_user_language
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise
