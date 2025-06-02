import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
import translation_model
import chromadb

from langid import classify
from spacy import load
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.retrievers import VectorIndexRetriever
from chatbot import Settings, client
from prompt_templates import few_shot_prompt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
     allow_methods=["*"],
    allow_headers=["*"],
)

chat_engines = {}
session_states = {}
translator = translation_model.create_text_translation_client_with_credential()
documents = SimpleDirectoryReader("data").load_data()
# db  = chromadb.PersistentClient(path="./chroma_db")
# chroma_collection = db.get_or_create_collection("MediChat")
# vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
# storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model ,llm=client)
response_synthesizer = get_response_synthesizer(response_mode="refine")
retriever = VectorIndexRetriever(index=index)
query_engine = RetrieverQueryEngine(retriever=retriever, response_synthesizer=response_synthesizer)

nlp = load("en_core_web_sm")

# Map full state names to 2-letter codes
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

def apply_guardrails(response_text:str) -> str:

    fallback = "\n\nTo help you better, please provide more specific details like your location or the kind of help you need."
    danger_phrases = ["can you clarify", "not sure", "please rephrase", "need more information"]
    too_short = len(response_text.strip()) < 20

    if any(phrase in response_text.lower() for phrase in danger_phrases) or too_short:
        return response_text.strip() + fallback
    
    return response_text.strip()

def extract_state_from_text(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":  # GPE = Geo-Political Entity
            state_name = ent.text.lower().strip()
            if state_name in STATE_NAME_TO_CODE:
                return STATE_NAME_TO_CODE[state_name]
    return None

class QueryRequest(BaseModel):
    session_id: str
    query: str

@app.post("/query")

async def query_llama(request: QueryRequest):

    session_id = request.session_id

      # Step 1: Detect the language of the question
    if session_id not in chat_engines:
        chat_engines[session_id] = CondenseQuestionChatEngine.from_defaults(query_engine=query_engine, lm=client, memory= ChatMemoryBuffer.from_defaults(), chat_prompt=few_shot_prompt)

    language, confidence = classify(request.query)
    if confidence < 0.75:
        return "Can you rephrase that? I couldn't confidently detect the language."

    # Step 2: If not English, translate the question
    if language != 'en':
        translated_question = translator.translate(body=[request.query], to_language=['en'], from_language=language)[0].translations[0].text
    else:
        translated_question = request.query
    
    if session_id not in session_states:
        guessed_state = extract_state_from_text(translated_question)
        if not guessed_state:
            return "To provide accurate resources, could you tell me what state you're in?"
        session_states[session_id] = guessed_state

    user_state = session_states[session_id]

    # Step 3: Set up a filtered query engine based on state
    filtered_retriever = VectorIndexRetriever(index=index, filters={"states": user_state})
    state_query_engine = RetrieverQueryEngine(retriever=filtered_retriever, response_synthesizer=response_synthesizer)

    # Update chat engine's underlying query engine (per user state)
    chat_engines[session_id]._query_engine = state_query_engine


    # Step 3: Use LlamaIndex to answer the question
    answer_in_english = chat_engines[session_id].chat(translated_question)

    safe_english_answer = apply_guardrails(answer_in_english.response)

    # #Step 4: Translate the answer back to the original language
    if language != 'en':
        answer_in_user_language = translator.translate(body=[safe_english_answer], from_language='en', to_language=[language])[0].translations[0].text
    else:
        answer_in_user_language = safe_english_answer

    return(answer_in_user_language)

