import os  
import base64
from openai import AzureOpenAI  

endpoint = os.getenv("ENDPOINT_URL", "https://medichatbot-openai.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "medichat-gpt-35-turbo")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")  

# Initialize Azure OpenAI Service client with key-based authentication    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",
)
    
    

#Prepare the chat prompt 
chat_prompt = [
    {
        "role": "system",
        "content": "You are a jovial customer support representative."
    }
] 
    
# Include speech result if speech is enabled  
messages = chat_prompt  
    
# Generate the completion  
completion = client.chat.completions.create(  
    model=deployment,
    messages=messages,
    max_tokens=800,  
    temperature=0.7,  
    top_p=0.95,  
    frequency_penalty=0,  
    presence_penalty=0,
    stop=None,  
    stream=False
)

print(completion.to_json())  
    