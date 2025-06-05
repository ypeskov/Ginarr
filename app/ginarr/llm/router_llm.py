from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from app.config.settings import settings  # contains OPENAI_API_KEY


# Prompt: instructing the model to act as a router
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "Ты маршрутизатор. Получаешь пользовательский запрос и выбираешь, что с ним делать. "
                "Ответь только ОДНИМ словом, без пояснений. Возможные опции: memory, tool, llm, write."
                "Пояснения: memory - поиск в памяти, tool - вызов инструмента, llm - вызов LLM, write - запись в память."
                "Если однозначно нельзя определить, то ответь llm."
            ),
        ),
        ("user", "{input}"),
    ]
)

llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=settings.OPENAI_API_KEY)

router_llm: Runnable = prompt | llm | (lambda msg: {"route": msg.content.strip().lower()})
