import os
import base64

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import ServiceContext, DocumentSummaryIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.azure_inference import AzureAIEmbeddingsModel
# from llama_index.llms.azure_inference import AzureAICompletionsModel

def Chat():

    endpoint = os.getenv("ENDPOINT_URL", "https://medichatbot-openai.openai.azure.com/")  
    deployment = os.getenv("DEPLOYMENT_NAME", "medichat-gpt-35-turbo")  
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")  

    # Initialize Azure OpenAI Service client with key-based authentication    
    client = AzureOpenAI(  
        azure_endpoint=endpoint,  
        api_key=subscription_key,  
        api_version="2024-08-01-preview",
        engine=deployment,
        deployment_name=deployment,
        model="gpt-3.5-turbo-0125"
    )
    
    # llm = AzureAICompletionsModel(
    # endpoint="https://medichatbot-openai.openai.azure.com/openai/deployments/medichat-gpt-35-turbo",
    # credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
    # api_version="2024-08-01-preview",
    # )
    # llm = AzureOpenAI(
    #     deployment_name="medichat-gpt-35-turbo",  # Your model deployment name
    #     model="gpt-35-turbo",  # Model type
    #     api_key=os.environ["AZURE_OPENAI_API_KEY"],
    #     azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    #     api_version="2024-08-01-preview",
    # )
    # service_context = ServiceContext.from_defaults(llm=llm)
    Settings.llm = client
    Settings.embed_model = AzureAIEmbeddingsModel(model="text-embedding-ada-002",endpoint="https://medichatbot-openai.openai.azure.com/openai/deployments/medichat-text-embedding-ada-002", api_key=subscription_key, deployment="medichat-text-embedding-ada-002", api_version="2023-05-15")
    documents = SimpleDirectoryReader("data").load_data()
    index = DocumentSummaryIndex.from_documents(documents, embed_model=Settings.embed_model ,llm=client)
    query_engine = index.as_query_engine()
    response = query_engine.query("What is this document about?")
    # messages = [
    # ChatMessage(
    #     role="system", content="You are a bot that responds to messages"
    #     ),
    #     ChatMessage(role="user", content="Hello"),
    #     ]
    # response = llm.chat(messages)
    return response


response = Chat()
print(response)