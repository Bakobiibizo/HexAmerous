from openai.types.beta.threads import ThreadMessage
from data_models import run
from openai.pagination import SyncCursorPage
from utils.tools import ActionItem, Actions, actions_to_map
from utils.openai_clients import litellm_client, assistants_client
import os
from utils.coala import CoALA


class OrchestratorAgent:
    def __init__(
        self,
        run_id: str,
        thread_id: str,
        tool_items: dict[str, ActionItem],
        job_summary: str,
    ):
        self.run_id = run_id
        self.thread_id = thread_id
        self.tool_items = tool_items
        self.action_items = actions_to_map(
            [Actions.TEXT_GENERATION.value, Actions.COMPLETION.value]
        )
        self.job_summary = job_summary

    def generate(
        self, messages: SyncCursorPage[ThreadMessage], runsteps: SyncCursorPage[run.RunStep]
    ) -> Actions:
        """
        Generate a summary of the chat history with a focus on the current user request and tool usage.

        Args:
            messages (SyncCursorPage[Message]): The chat messages.
            runsteps (SyncCursorPage[run.RunStep]): The run steps.

        Returns:
            Actions: The action to be taken based on the generated summary.
        """
        # Compose the prompt for the summarization task
        coala = CoALA(
            runsteps=runsteps,
            messages=messages,
            job_summary=self.job_summary,
            tools_map=self.tool_items,
        )
        prompt = coala.compose_prompt("action")
        print("\n\nORCHESTRATOR COALA PROMPT:\n", prompt)

        generator_messages = [
            {
                "role": "user",
                "content": prompt,
            },
        ]

        # Call to the AI model to generate the summary
        response = litellm_client.chat.completions.create(
            model=os.getenv("LITELLM_MODEL"),  # Replace with your model of choice
            messages=generator_messages,
            max_tokens=100,  # You may adjust the token limit as necessary
        )
        content = response.choices[0].message.content
        content = content.replace("\\", "")
        print("ORCHESTRATOR GENERATION: ", response.choices[0].message.content)
        for key in self.tool_items.keys():
            if f"{key}" in content:
                print("KEY: ", f"<{key}>")
                return Actions(key)
        for key in self.action_items.keys():
            if f"{key}" in content:
                print("KEY: ", f"<{key}>")
                return Actions(key)

        return Actions.FAILURE
