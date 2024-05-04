from utils.ops_api_handler import create_web_retrieval_runstep
from utils.openai_clients import litellm_client
from utils.basic_retriever import retriever1
from data_models import run
import os

# import coala
from agents import coala


class WebRetrieval:
    def __init__(
        self,
        coala_class: "coala.CoALA",
    ):
        self.coala_class = coala_class

    def generate(
        self,
    ) -> run.RunStep:
        # get relevant retrieval query

        instructions = f"""Your role is generate a query for semantic search according to current working memory.
Even if there is no relevant information in the working memory, you should still generate a query to retrieve the most relevant information from the University of Florida (UF).
Only respond with the query iteself NOTHING ELSE.

"""  # noqa

        messages = [
            {
                "role": "user",
                "content": instructions + self.compose_query_system_prompt(),
            },
        ]
        response = litellm_client.chat.completions.create(
            model=os.getenv("LITELLM_MODEL"),
            messages=messages,
            max_tokens=200,
        )
        query = response.choices[0].message.content

        # Retrieve documents based on the query
        retrieved_documents = retriever1.invoke(query)
        retrieved_documents = [doc.page_content for doc in retrieved_documents]

        run_step = create_web_retrieval_runstep(
            self.coala_class.thread_id,
            self.coala_class.run_id,
            self.coala_class.assistant_id,
            retrieved_documents,
            site="https://www.ufl.edu/",
        )
        return run_step

    def compose_query_system_prompt(self) -> str:
        trace = self.coala_class.compose_react_trace()

        composed_instruction = f"""Current working memory:
{trace}"""
        return composed_instruction
