import os
from langchain.llms import OpenAI
from dotenv import load_dotenv
from src.helpers.datastax_vectordb import (
    ASTRA_DB_KEYSPACE,
)

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = OpenAI(openai_api_key=OPENAI_API_KEY)



prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"]
)

chain = llm.create_chain(prompt=prompt)