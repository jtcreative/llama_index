import os
import base64

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
# from llama_index.llms.azure_inference import AzureAICompletionsModel
endpoint = os.getenv("ENDPOINT_URL", "https://medichatbot-openai-eastus2.openai.azure.com")  
deployment = os.getenv("DEPLOYMENT_NAME", "medichat-gpt-35-turbo")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")  
# Initialize Azure OpenAI Service client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-08-01-preview",
    engine=deployment,
    deployment_name=deployment,
    model="gpt-3.5-turbo-0125",
    system_prompt="""
    You are an intelligent assistant that helps users retrieve accurate and context-aware information from a curated knowledge base.

    Your role is to:
    1. Ask the user clarifying questions to collect all relevant details — especially location-based information like state or zip code, or other necessary filters.
    2. Once enough information is gathered, search the provided context to find the most relevant answer.
    3. Respond clearly and concisely, citing the source website address if possible.

    Rules:
    - Only answer questions based on the provided context.
    - If the context is not sufficient or the user hasn't provided enough detail, ask follow-up questions before attempting an answer.
    - Do NOT make up information. If something is missing, ask or say "I'm not sure based on the available information."
    - Always tailor answers to the user's location or region when applicable.
    """
)
#Initialize Azure OpenAI embedding model
Settings.llm = client
Settings.embed_model = AzureOpenAIEmbedding(model="text-embedding-ada-002",endpoint=endpoint, api_key=subscription_key, deployment_name="medichat-text-embedding-ada-002", deployment="medichat-text-embedding-ada-002", api_version="2023-05-15")




