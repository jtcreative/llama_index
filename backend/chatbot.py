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
    model="gpt-3.5-turbo-0125"
)
#Initialize Azure OpenAI embedding model
Settings.llm = client
Settings.embed_model = AzureOpenAIEmbedding(model="text-embedding-ada-002",endpoint=endpoint, api_key=subscription_key, deployment_name="medichat-text-embedding-ada-002", deployment="medichat-text-embedding-ada-002", api_version="2023-05-15")




