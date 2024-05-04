import json
from typing import Optional
from openai.types.beta.threads import ThreadMessage
from openai.pagination import SyncCursorPage
from utils.weaviate_utils import retrieve_file_chunks
from utils.ops_api_handler import create_retrieval_runstep
from utils.tools import ActionItem, Actions, actions_to_map
from utils.openai_clients import litellm_client, assistants_client
from data_models import run
import os

# import coala
from agents import coala


class Retrieval:
    def __init__(
        self,
        coala_class: "coala.CoALA",
    ):
        self.coala_class = coala_class

    def generate(
        self,
    ) -> run.RunStep:
        # get relevant retrieval query

        instruction = f"""Your role is generate a query for semantic search to retrieve important according to current working memory and the available files.
Even if there is no relevant information in the working memory, you should still generate a query to retrieve the most relevant information from the available files.
Only respond with the query iteself NOTHING ELSE.

"""
        messages = [
            {
                "role": "user",
                "content": instruction + self.compose_query_system_prompt(),
            },
        ]
        response = litellm_client.chat.completions.create(
            model=os.getenv("LITELLM_MODEL"),  # Replace with your model of choice
            messages=messages,
            max_tokens=200,  # You may adjust the token limit as necessary
        )
        query = response.choices[0].message.content
        # TODO: retrieve from db, and delete mock retrieval document
        retrieved_documents = retrieve_file_chunks(
            self.coala_class.assistant.file_ids, query
        )

        run_step = create_retrieval_runstep(
            self.coala_class.thread_id,
            self.coala_class.run_id,
            self.coala_class.assistant_id,
            retrieved_documents,
        )
        return run_step

    def compose_file_list(
        self,
    ) -> str:
        files_names = []
        for file_id in self.coala_class.assistant.file_ids:
            file = assistants_client.files.retrieve(file_id)
            files_names.append(f"- {file.filename}")
        return "\n".join(files_names)

    def compose_query_system_prompt(self) -> str:
        trace = self.coala_class.compose_react_trace()

        composed_instruction = f"""The files currently available to you are:
{self.compose_file_list()}

Current working memory:
{trace}"""
        return composed_instruction
