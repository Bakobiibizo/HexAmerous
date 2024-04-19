import json
from typing import Optional
from openai.types.beta.threads import Message
from openai.pagination import SyncCursorPage
from utils.ops_api_handler import create_message_runstep
from utils.tools import ActionItem, Actions, actions_to_map
from utils.openai_clients import litellm_client, assistants_client
from data_models import run


class TextGeneration:
    def __init__(
        self, run_id: str, thread_id: str, assistant_id: str, job_summary: str
    ):
        self.role_instructions = f"""Your role is to provide a text response to the user according to the messages and the current working memory."""
        self.run_id = run_id
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.job_summary = job_summary

    def generate(self, content: Optional[str] = None) -> run.RunStep:
        if not content:
            messages = [
                {
                    "role": "system",
                    "content": self.compose_system_prompt(),
                },
                {
                    "role": "user",
                    "content": self.job_summary,
                },
            ]
            response = litellm_client.chat.completions.create(
                model="mixtral",  # Replace with your model of choice
                messages=messages,
                max_tokens=500,  # You may adjust the token limit as necessary
            )
            content = response.choices[0].message.content
        run_step = create_message_runstep(self.thread_id, self.run_id, self.assistant_id, content)
        print("TextGeneration content: ", response.choices[0].message.content)
        return run_step

    def compose_working_memory(
        self,
    ) -> str:
        steps = assistants_client.beta.threads.runs.steps.list(
            thread_id=self.thread_id,
            run_id=self.run_id,
        )
        return "\n".join(
            [json.dumps(step.step_details.model_dump()) for step in steps.data]
        )

    def compose_system_prompt(self) -> str:
        working_memory = self.compose_working_memory()

        composed_instruction = f"""{self.role_instructions}

Current working memory:
{working_memory}"""
        print("\n\nTEXTGENERATION SYSTEM PROMP: ", composed_instruction)
        return composed_instruction
