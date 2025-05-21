import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
import translation_model
import chromadb

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from langdetect import detect
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.retrievers import VectorIndexRetriever
from chatbot import Settings, client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
     allow_methods=["*"],
    allow_headers=["*"],
)

chat_engines = {}
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

class QueryRequest(BaseModel):
    session_id: str
    query: str

@app.post("/query")

async def query_llama(request: QueryRequest):

    session_id = request.session_id

      # Step 1: Detect the language of the question
    if session_id not in chat_engines:
        chat_engines[session_id] = CondenseQuestionChatEngine.from_defaults(query_engine=query_engine, lm=client, memory= ChatMemoryBuffer.from_defaults())
        
    language = detect(request.query)

    # Step 2: If not English, translate the question
    if language != 'en':
        translated_question = translator.translate(body=[request.query], to_language=['en'], from_language=language)[0].translations[0].text
    else:
        translated_question = request.query

    # Step 3: Use LlamaIndex to answer the question
    answer_in_english = chat_engines[session_id].chat(translated_question)

    # #Step 4: Translate the answer back to the original language
    if language != 'en':
        answer_in_user_language = translator.translate(body=[answer_in_english.response], from_language='en', to_language=[language])[0].translations[0].text
    else:
        answer_in_user_language = answer_in_english

    return(answer_in_user_language)