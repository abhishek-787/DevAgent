from langchain_ollama import ChatOllama

from app.core.config import settings


coding_model = ChatOllama(
    model=settings.coding_model,
    base_url=settings.ollama_base_url,
    temperature=0,
    reasoning=False,
    # num_predict=512,
    num_ctx=8192,
)