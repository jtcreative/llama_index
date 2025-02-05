import logging
import sys
import os


def create_text_translation_client_custom_with_credential():
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import AzureKeyCredential

    endpoint = os.environ["AZURE_TEXT_TRANSLATION_ENDPOINT"]
    apikey = os.environ["AZURE_TEXT_TRANSLATION_APIKEY"]
    # [START create_text_translation_client_custom_with_credential]
    credential = AzureKeyCredential(apikey)
    text_translator = TextTranslationClient(credential=credential, endpoint=endpoint)
    # [END create_text_translation_client_custom_with_credential]
    return text_translator