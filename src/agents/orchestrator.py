from openai.types.beta.threads import Message
from openai.pagination import SyncCursorPage
from utils.tools import ActionItem, Actions, actions_to_map
from utils.openai_clients import litellm_client, assistants_client
import json


class OrchestratorAgent:
    def __init__(
        self,
        run_id: str,
        thread_id: str,
        tools: dict[str, ActionItem],
        job_summary: str,
    ):
        self.run_id = run_id
        self.thread_id = thread_id
        self.tool_items = tools
        self.action_items = actions_to_map(
            [Actions.TEXT_GENERATION.value, Actions.COMPLETION.value]
        )
        self.job_summary = job_summary
        self.role_instructions = f"""Your role is to determine which tool to use next according to the episodic memory (current conversation) and working memory.
In addition to the tools, you can also be able to use actions.
You must reply with the corresponding key of the tool or action you think should be used next to fulfill the user request.
The next tool or action must be formated as `<tool_or_action>`, only reply with the tool or action to use.
You should never continue a `<{Actions.TEXT_GENERATION.value}>` with another `<{Actions.TEXT_GENERATION.value}>`.
You will always finish with `<{Actions.COMPLETION.value}>` but try and use `<{Actions.TEXT_GENERATION.value}>` before completing.
If the amount of working memory is too large and no process seems to be made then use `<{Actions.COMPLETION.value}>` to end the conversation."""

    def generate(self) -> Actions:
        """
        Create a summary of the chat history with an emphasis on the current user request and tool use.

        Args:
            tools (dict): A dictionary containing available tools and their descriptions.
            chat_history (list): A list of messages representing the chat history.

        Returns:
            str: A summary useful for planning and tool use.
        """
        # Compose the prompt for the summarization task
        system_prompt = self.compose_system_prompt()

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": self.job_summary,
            },
        ]

        # Call to the AI model to generate the summary
        response = litellm_client.chat.completions.create(
            model="mixtral",  # Replace with your model of choice
            messages=messages,
            max_tokens=100,  # You may adjust the token limit as necessary
        )
        content = response.choices[0].message.content
        content = content.replace("\\", "")
        print("ORCHESTRATOR GENERATION: ", response.choices[0].message.content)
        for key in self.tool_items.keys():
            if f"<{key}>" in content:
                print("KEY: ", f"<{key}>")
                return Actions(key)
        for key in self.action_items.keys():
            if f"<{key}>" in content:
                print("KEY: ", f"<{key}>")
                return Actions(key)

        return Actions.FAILURE

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

        tools_list = "\n".join(
            [
                f"- <{tool.type}>: {tool.description}"
                for _, tool in self.tool_items.items()
            ]
        )

        print("Action Items: ", self.action_items)
        actions_list = "\n".join(
            [
                f"- <{action.type}>: {action.description}"
                for _, action in self.action_items.items()
            ]
        )

        composed_instruction = f"""{self.role_instructions}

Current working memory:
{working_memory}

The actions available to you are:
{actions_list}

The tools available to you are:
{tools_list}"""
        print("\n\nORCHESTRATION SYSTEM PROMP: ", composed_instruction)
        return composed_instruction
