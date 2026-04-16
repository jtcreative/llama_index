# -*- coding: utf-8 -*-
"""
Language detection and translation utilities
"""

import logging
import fasttext
from typing import Tuple
from .config import ChatbotConfig

logger = logging.getLogger(__name__)

_lang_model = None
_translator = None


def get_language_model():
    """Lazy-load language detection model"""
    global _lang_model
    if _lang_model is None:
        try:
            model_path = ChatbotConfig.get_model_path()
            logger.info(f"Loading language detection model from {model_path}")
            _lang_model = fasttext.load_model(model_path)
            logger.info("Language model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load language model: {e}")
            raise
    return _lang_model


def get_translator():
    """Lazy-load translator client"""
    global _translator
    if _translator is None:
        try:
            from translation_model import create_text_translation_client_with_credential
            logger.info("Initializing translation client")
            _translator = create_text_translation_client_with_credential()
            logger.info("Translation client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize translator: {e}")
            raise
    return _translator


def detect_language(text: str) -> Tuple[str, float]:
    """
    Detect language of text.
    
    Args:
        text: Input text to detect language for
        
    Returns:
        Tuple of (language_code, confidence)
    """
    try:
        model = get_language_model()
        labels, confidences = model.predict(text, k=1)
        lang_code = labels[0].replace("__label__", "")
        confidence = float(confidences[0])
        logger.debug(f"Detected language: {lang_code} (confidence: {confidence})")
        return lang_code, confidence
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        raise


def translate_text(text: str, target_language: str, source_language: str = "en") -> str:
    """
    Translate text to target language.
    
    Args:
        text: Text to translate
        target_language: Target language code
        source_language: Source language code (default: en)
        
    Returns:
        Translated text
    """
    if target_language == source_language:
        return text
        
    try:
        translator = get_translator()
        result = translator.translate(
            body=[text],
            to_language=[target_language],
            from_language=source_language if source_language != "en" else None
        )
        translated = result[0].translations[0].text
        logger.debug(f"Translated from {source_language} to {target_language}")
        return translated
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise
