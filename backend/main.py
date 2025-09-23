import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
import translation_model
import chromadb

import fasttext
import redis
from redisMemory import RedisChatMemory
from spacy import load
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage import StorageContext
from llama_index.core.node_parser import SimpleNodeParser
from chatbot import Settings, client
from prompt_templates import few_shot_prompt
from botbuilder.schema import Activity
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext, activity_handler
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
     allow_methods=["*"],
    allow_headers=["*"],
)

APP_ID = os.environ.get("MICROSOFT_APP_ID")
APP_PASSWORD = os.environ.get("MICROSOFT_APP_PASSWORD")
TENANT_ID = os.environ.get("MICROSOFT_TENANT_ID")

model_path = os.path.join(os.path.dirname(__file__), "..", "models", "lid.176.bin")
print("DEBUG: Fetching language detection model from: ", model_path)
lang_model = fasttext.load_model(model_path)

if APP_ID and APP_PASSWORD:
    print("DEBUG: Using credentials for Bot Framework Adapter")
    adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD, TENANT_ID)
    
else:
    # No credentials → allow emulator to connect without tokens
    adapter_settings = BotFrameworkAdapterSettings(None, None)

adapter = BotFrameworkAdapter(adapter_settings)
adapter.use_websocket = True
adapter.settings.trust_service_url = "https://webchat.botframework.com/"

r = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
def get_session_state(session_id: str):
    return r.get(f"state:{session_id}")

def set_session_state(session_id: str, state: str, ttl=3600):
    r.setex(f"state:{session_id}", ttl, state)  # expire after 1h
chat_engines = {}
session_states = {}
translator = translation_model.create_text_translation_client_with_credential()


chroma_client = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = chroma_client.get_or_create_collection("MediChat")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

if(chroma_collection.count() > 0):
    print("DEBUG: Loading existing index from ChromaDB")
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=Settings.embed_model ,llm=client, storage_context=storage_context)
else:
    parser = SimpleNodeParser.from_defaults(chunk_size=1500, chunk_overlap=100)
    documents = parser.get_nodes_from_documents(SimpleDirectoryReader("data").load_data())
    print("DEBUG: Creating new index and persisting to ChromaDB")
    index = VectorStoreIndex(documents, embed_model=Settings.embed_model ,llm=client, storage_context=storage_context)
    index.storage_context.persist()
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
    print("DEBUG: Named entities found:", [(ent.text, ent.label_) for ent in doc.ents])
    for ent in doc.ents:
        if ent.label_ == "GPE":  # GPE = Geo-Political Entity
            state_name = ent.text.lower().strip()
            if state_name in STATE_NAME_TO_CODE:
                return STATE_NAME_TO_CODE[state_name]
    return None


def detect_language(text: str):
    labels, confidences = lang_model.predict(text, k=1)
    lang_code = labels[0].replace("__label__", "")
    return lang_code, float(confidences[0])

class QueryRequest(BaseModel):
    session_id: str
    query: str


@app.post("/query")

async def query_llama(request: QueryRequest):

    session_id = request.session_id
    print(f"DEBUG: Received query from session {session_id}: {request.query}")


    clean_query = request.query.strip().lower()
    language, confidence = detect_language(clean_query)
    print(f"DEBUG: Detected language {language} with confidence {confidence}")

    if confidence < 0.2:
        return "Can you rephrase that? I couldn't confidently detect the language."

    # # Step 1: If not English, translate the question
    if language != 'en':
        translated_question = translator.translate(body=[request.query], to_language=['en'], from_language=language)[0].translations[0].text
    else:
        translated_question = request.query
    
    # Step 2: Restore short-term memory from Redis
    memory_key = f"chat:{session_id}"
    memory = RedisChatMemory(redis_client=r, key=memory_key)

    # Step 3: Build a fresh chat engine with memory
    chat_engine = CondenseQuestionChatEngine.from_defaults(
        query_engine=query_engine,
        lm=client,
        memory=memory,
        chat_prompt=few_shot_prompt
    )

    # if session_id not in session_states:
    #     guessed_state = extract_state_from_text(translated_question)
    #     if not guessed_state:
    #         safe_english_answer = "To provide accurate resources, could you tell me what state you're in?"
    #         if language != 'en':
    #             answer_in_user_language = translator.translate(body=[safe_english_answer], from_language='en', to_language=[language])[0].translations[0].text
    #         else:
    #             answer_in_user_language = safe_english_answer

    #         return answer_in_user_language
    #     session_states[session_id] = guessed_state

    # user_state = session_states[session_id]

    # Step 4: Set up a filtered query engine based on state
    # filtered_retriever = VectorIndexRetriever(index=index, filters={"coverage_area": user_state})
    # state_query_engine = RetrieverQueryEngine(retriever=filtered_retriever, response_synthesizer=response_synthesizer)

    # # Update chat engine's underlying query engine (per user state)
    # chat_engines[session_id]._query_engine = state_query_engine


    # Step 5: Use LlamaIndex to answer the question
    answer_in_english = chat_engine.chat(translated_question)
    answer_text = apply_guardrails(answer_in_english.response)

    # Step 5: Save new Q&A back to Redis with expiry (e.g., 30 mins)
    memory.append("user", translated_question)
    memory.append("assistant", answer_text)
    r.expire(memory_key, 1800)

    # #Step 6: Translate the answer back to the original language
    if language != 'en':
        answer_in_user_language = translator.translate(body=[answer_text], from_language='en', to_language=[language])[0].translations[0].text
    else:
        answer_in_user_language = answer_text

    print(f"DEBUG: Final answer to user: {answer_in_user_language}")
    return(answer_in_user_language)

@app.post("/api/messages")
async def receive_bot_message(req: Request):
        
    body = await req.json()
    activity = Activity().deserialize(body)

    auth_header = req.headers.get("Authorization", "")
    # activity.service_url = "http://localhost:50936"
    print("DEBUG: serviceUrl = ", activity.service_url)

    async def aux_func(turn_context: TurnContext):
        
        user_text = activity.text or ""
        user_id = activity.from_property.id if activity.from_property else "unknown_user"

        if not user_text:
            print("DEBUG: No text in activity")
            # await turn_context.send_activity("Please enter a message.")
            return

        if "test" in user_text.lower():
            print("DEBUG: Test message received")
            await turn_context.send_activity("Test successful! I see your message.")
            return
        
        query_request = QueryRequest(session_id=user_id, query=user_text)
        response = await query_llama(query_request)
        await turn_context.send_activity(str(response))

    # Process the incoming activity with the adapter
    return await adapter.process_activity(activity, auth_header, aux_func)


#uvicorn main:app --reload --port 3978