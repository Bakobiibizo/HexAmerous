import json
from typing import Optional
from openai.types.beta.threads import ThreadMessage
from openai.pagination import SyncCursorPage
from utils.coala import CoALA
from utils.ops_api_handler import create_message_runstep
from utils.tools import ActionItem, Actions, actions_to_map
from utils.openai_clients import litellm_client, assistants_client
from data_models import run
import os


class TextGeneration:
    def __init__(
        self,
        run_id: str,
        thread_id: str,
        assistant_id: str,
        tool_items: dict[str, ActionItem],
        job_summary: str,
    ):
        self.role_instructions = f"""Your role is to provide a text response to the user according to the messages and the current working memory."""
        self.run_id = run_id
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.tool_items = tool_items
        self.job_summary = job_summary

    def generate(
        self,
        messages: SyncCursorPage[ThreadMessage],
        runsteps: SyncCursorPage[run.RunStep],
        content: Optional[str] = None,
    ) -> run.RunStep:
        if not content:
            # Compose the prompt for the summarization task
            coala = CoALA(
                runsteps=runsteps,
                messages=messages,
                job_summary=self.job_summary,
                tools_map=self.tool_items,
            )
            prompt = coala.compose_prompt("thought")
            print("\n\nTEXTGENERATOR COALA PROMPT:\n", prompt)

            generator_messages = [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
            response = litellm_client.chat.completions.create(
                model=os.getenv("LITELLM_MODEL"),  # Replace with your model of choice
                messages=generator_messages,
                max_tokens=500,  # You may adjust the token limit as necessary
            )
            content = response.choices[0].message.content
            print("\n\nTEXTGENERATOR RESPONSE:\n", content)
            content = content.split("Thought:", 1)[1]
            print("\n\nTEXTGENERATOR RESPONSE SPLIT:\n", content)
            content = content.split("Action:", 1)[0]

        run_step = create_message_runstep(
            self.thread_id, self.run_id, self.assistant_id, content
        )
        print("TextGeneration content: ", content)
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
