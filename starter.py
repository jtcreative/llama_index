import logging
import sys
import translation_model

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from langdetect import detect
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader


translator = translation_model.create_text_translation_client_with_credential()
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)


def answer_question_in_language(question):
    # Step 1: Detect the language of the question
    language = detect(question)
    
    # Step 2: If not English, translate the question
    if language != 'en':
        translated_question = translator.translate(body=[question], to_language=['en'], from_language=language)
    else:
        translated_question = question

    # Step 3: Use LlamaIndex to answer the question
    answer_in_english = index.query(translated_question)
    
    # #Step 4: Translate the answer back to the original language
    if language != 'en':
        answer_in_user_language = translator.translate(answer_in_english, src='en', dest=language).text
    else:
        answer_in_user_language = answer_in_english

    return translated_question

# Example Usage
#english
#response = query_engine.query("What did the author do growing up?")
#spanish
question = "¿Qué hizo el autor cuando era niño?"
# question = "What did the author do when he was a kid?"
response = answer_question_in_language(question)
print(response)  # Should output in Spanish