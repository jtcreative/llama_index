from llama_index.core.prompts import ChatPromptTemplate, ChatMessage

few_shot_prompt = ChatPromptTemplate(messages=[
    ChatMessage(role="system", content="You are an intelligent assistant that helps users retrieve accurate and context-aware information from a curated knowledge base."),
    ChatMessage(role="user", content="How can I get health insurance?"),
    ChatMessage(role="assistant", content="If you're in Texas, you can visit [Healthcare.gov](http://www.healthcare.gov), a federal platform that provides health insurance options. This program is available in your state."),
    ChatMessage(role="user", content="Where can I apply for health benefits?"),
    ChatMessage(role="assistant", content="Texans can apply for coverage through [Healthcare.gov](http://www.healthcare.gov), which is supported in Texas by the U.S. Centers for Medicare & Medicaid Services."),
    ChatMessage(role="user", content="{query_str}"),
])