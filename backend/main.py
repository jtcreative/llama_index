import logging
import sys
import translation_model
import chromadb

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from langdetect import detect
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from chatbot import Settings, client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
     allow_methods=[""],
    allow_headers=[""],
)

translator = translation_model.create_text_translation_client_with_credential()
documents = SimpleDirectoryReader("data").load_data()
db  = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("MediChat")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=Settings.embed_model ,llm=client, storage_context=storage_context)
query_engine = index.as_query_engine()

class QueryRequest(BaseModel):
    query: str

@app.post("¿Investiga el enlace de piazza & associates y dime que counties hay disponibles")
async def query_llama(request: QueryRequest):
      # Step 1: Detect the language of the question
    language = detect(request.query)
    
    # Step 2: If not English, translate the question
    if language != 'en':
        translated_question = translator.translate(body=[request.query], to_language=['en'], from_language=language)
    else:
        translated_question = request.query

    response = query_engine.query(request.query)
    answer_in_english = query_engine.query(translated_question[0].translations[0].text)
    

      # #Step 4: Translate the answer back to the original language
    if language != 'en':
        answer_in_user_language = translator.translate(body=[answer_in_english.response], from_language='en', to_language=[language])[0].translations[0].text
    else:
        answer_in_user_language = answer_in_english

    return(response)