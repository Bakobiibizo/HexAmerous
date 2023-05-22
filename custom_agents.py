import queue
from chatgpt import GPTChatbot
from embeddings import load_vector_store_docs, OpenAIEmbeddings
from dotenv import load_dotenv
from langchain import Wikipedia
from langchain.agents import Tool
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.agents.react.base import DocstoreExplorer


load_dotenv()

class CustomAgents():
    def __init__(self, gpt_chatbot):
        self.gpt_chatbot = gpt_chatbot
        self.docstore = DocstoreExplorer(Wikipedia())
        self.gpt_chatbot = GPTChatbot(queue.Queue())
        self.embeddings = OpenAIEmbeddings()
        self.tools = [
            Tool(
                name="Search",
                func=self.docstore.search,
                description="useful for when you need to ask with search",
            ),
            Tool(
                name="Lookup",
                func=self.docstore.lookup,
                description="useful for when you need to ask with lookup",
            ),
        ]
        self.metadata_field_info = [
            AttributeInfo(
                name="README.md",
                description="readme file for the hexamerous project",
                type="string or list[string]",
            )
        ]
        self.document_content_description = "a readme file from a python project called hexamerous."

    def base_retriever(self, user_query):
        vectorstore = load_vector_store_docs()
        retriever = SelfQueryRetriever.from_llm(
            self.llm,
            vectorstore,
            self.document_content_description,
            self.metadata_field_info,
            verbose=True,
        )
        docs = retriever.get_relevant_documents(user_query)
        print(docs)
        return docs


    def data_base_memory_search(self, user_query):
        docs = self.base_retriever(user_query)
        messages = {
            "role": "system",
            "content": f"""
            "The user has asked this question:

            {user_query}

            You have looked up the relevant information from your data store and it is:

            {docs}

            Please answer the user's question using the data as relevant context."
            """
        }
        print(messages)

        new_messages = self.gpt_chatbot.get_messages(messages)

        result = self.gpt_chatbot.get_response(new_messages, "gpt-4")

        print(f"Memory search result: {result}")

        return result
