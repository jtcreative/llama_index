from llama_index.core.prompts import ChatPromptTemplate, ChatMessage

few_shot_prompt = ChatPromptTemplate(messages=[
    ChatMessage(role="system", content="You are an intelligent assistant that helps users retrieve accurate and context-aware information from a curated knowledge base."),
    ChatMessage(role="user", content="Where can I get legal help?"),
    ChatMessage(role="assistant", content="Try [HealthCare.gov](http://www.healthcare.gov)"),
    ChatMessage(role="user", content="I need housing support."),
    ChatMessage(role="assistant", content="Visit [HUD.gov](https://www.hud.gov/) or your state's housing authority."),
    ChatMessage(role="user", content="{query_str}"),
])