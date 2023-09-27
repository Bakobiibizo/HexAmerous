import os
from embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.tools import Tool
from langchain.docstore.wikipedia import Wikipedia
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.agents import Tool, AgentExecutor, BaseMultiActionAgent
from langchain import OpenAI, SerpAPIWrapper
from typing import List, Tuple, Any, Union
from langchain.schema import AgentAction, AgentFinish
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.agents.react.base import DocstoreExplorer
from embeddings import load_vector_store_docs
from chatgpt import GPTChatbot

docstore = InMemoryDocstore(Wikipedia())

docstore = DocstoreExplorer(Wikipedia())

search = SerpAPIWrapper()

llm = OpenAI(temperature=0)

embeddings = OpenAIEmbeddings()

chat_gpt = GPTChatbot()

tools = [
    Tool(
        name="Search Wiki",
        func=docstore.search,
        description="useful for when you need to ask for details on historical topics."
        ),
    Tool(name="Lookup",
         func=docstore.lookup,
         description="useful for when you need to look up details on historical topics."
         ),
    Tool(
        name = "Web Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    )
]




class MegAgent(BaseMultiActionAgent):
    """Meg Custom Agent."""

    @property
    def input_keys(self):
        return ["input"]

    def plan(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[List[AgentAction], AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        if not intermediate_steps:
            return [
                AgentAction(tool="Search", tool_input=kwargs["input"], log=""),
                AgentAction(tool="RandomWord", tool_input=kwargs["input"], log=""),
            ]
        else:
            return AgentFinish(return_values={"output": "bar"}, log="")

    async def aplan(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[List[AgentAction], AgentFinish]:
        """Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        if not intermediate_steps:
            return [
                AgentAction(tool="Search", tool_input=kwargs["input"], log=""),
                AgentAction(tool="RandomWord", tool_input=kwargs["input"], log=""),
            ]
        else:
            return AgentFinish(return_values={"output": "bar"}, log="")

load_dotenv()

metadata_field_info=[
    AttributeInfo(
        name='path',
        description='a number of documents stored and labeled by their path and name',
        type='string or list[string]'
    )
]

document_content_description = 'document store containing all docs labeled by path and name.'

def base_retriever(user_query):
    vectorstore = load_vector_store_docs()
    retriever = SelfQueryRetriever.from_llm(llm, vectorstore, document_content_description, metadata_field_info, verbose=True)
    docs = retriever.get_relevant_documents(user_query)
    print(docs)
    return docs




def data_base_memory_search(user_query):
    docs = base_retriever(user_query)
    prompt = {
        "role": "system",
        "content": '''
        "The user has asked this question:

        {query}

        You have looked up the relevant information from your data store and it is:

        {data}

        Please answer the user's question using the data as relevant context."
        '''.format(query=user_query, data=docs)
    }
    print(prompt)

    result = chat_gpt.get_response(prompt)

    print(f"Memory search result: {result}")

    return result
