import json
from typing import Optional
from openai.types.beta.threads import ThreadMessage
from openai.pagination import SyncCursorPage
from utils.weaviate_utils import retrieve_file_chunks
from utils.ops_api_handler import create_web_retrieval_runstep
from utils.tools import ActionItem, Actions, actions_to_map
from utils.openai_clients import litellm_client, assistants_client
from data_models import run
import os

# import coala
from utils.coala import CoALA


# TODO: Sean, update this, this is where the execution happens
class WebRetrieval:
    def __init__(
        self,
        run_id: str,
        thread_id: str,
        assistant_id: str,
        tools_map: dict[str, ActionItem],
        job_summary: str,
    ):
        self.query_maker_instructions = f"""Your role is generate a query for semantic search to retrieve important according to current working memory and the available files.
Even if there is no relevant information in the working memory, you should still generate a query to retrieve the most relevant information from the available files.
Only respond with the query iteself NOTHING ELSE.""" # TODO: Sean, bespoke prompt currently used for creating the retrieval query
        self.run_id = run_id
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.tool_items = tools_map
        self.job_summary = job_summary
        self.coala = None
        self.assistant = None

    def generate(
        self,
        messages: SyncCursorPage[ThreadMessage],
        runsteps: SyncCursorPage[run.RunStep],
        content: Optional[str] = None,
    ) -> run.RunStep:
        # get relevant retrieval query
        self.coala = CoALA(
            runsteps=runsteps,
            messages=messages,
            job_summary=self.job_summary,
            tools_map=self.tool_items,
        )

        messages = [
            {
                "role": "user",
                "content": self.compose_query_system_prompt(),
            },
        ]
        response = litellm_client.chat.completions.create(
            model=os.getenv("LITELLM_MODEL"),  # Replace with your model of choice
            messages=messages,
            max_tokens=200,  # You may adjust the token limit as necessary
        )
        query = response.choices[0].message.content
        print("Retrieval query: ", query)
        # TODO: retrieve from db, and delete mock retrieval document
        retrieved_documents = retrieve_file_chunks(self.assistant.file_ids, query)

        run_step = create_web_retrieval_runstep(  # TODO: Sean, this is important, this is how state is managed
            self.thread_id,
            self.run_id,
            self.assistant_id,
            retrieved_documents,
            site="INSERT_SITE_HERE",
        )
        return run_step

    def compose_query_system_prompt(self) -> str:
        trace = self.coala.compose_trace()

        composed_instruction = f"""{self.query_maker_instructions} 

Current working memory:
Question: {self.job_summary}
{trace}""" # TODO: Sean, this prompt should not change too much
        print("\n\nRETRIEVAL SYSTEM PROMP: ", composed_instruction)
        return composed_instruction
