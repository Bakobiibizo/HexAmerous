from openai.types.beta.threads import ThreadMessage
from openai.pagination import SyncCursorPage
from constants import PromptKeys
from utils.tools import ActionItem
from utils.openai_clients import litellm_client
import os


class RouterAgent:
    def __init__(
        self,
    ):
        self.role_instructions = f"""Your role is to determine whether to use tools or directly generate a response.
In the case that you think you may need more tools, simply respond with '{PromptKeys.TRANSITION.value}'. Otherwise, generate an appropriate response."""  # noqa

    def compose_system_prompt(self, tools: dict[str, ActionItem]) -> str:
        tools_list = "\n".join(
            [f"- {tool.type}: {tool.description}" for _, tool in tools.items()]
        )
        return f"""{self.role_instructions}

The tools available to you are:
{tools_list}"""

    # TODO: add assistant and base tools off of assistant
    def generate(
        self, tools: dict[str, ActionItem], paginated_messages: SyncCursorPage[ThreadMessage]
    ) -> str:
        """
        Generates a response based on the chat history and role instructions.

        Args:
            tools (dict): The tools available to the agent.
            paginated_messages (SyncCursorPage[Message]): The chat history.

        Returns:
            str: It either returns `{PromptKeys.TRANSITION.value}` or a generated response.
        """

        messages = [
            {
                "role": "system",
                "content": self.compose_system_prompt(tools),
            }
        ]
        print("\n\nSYSTEM PROMPT: ", messages[0]["content"])
        for message in paginated_messages.data:
            messages.append(
                {
                    "role": message.role,
                    "content": message.content[0].text.value,
                }
            )
        print("MESSAGES: ", messages)
        response = litellm_client.chat.completions.create(
            model=os.getenv("LITELLM_MODEL"),
            messages=messages,
            max_tokens=500,
        )

        print("GENERATION: ", response.choices[0].message.content)
        if PromptKeys.TRANSITION.value in response.choices[0].message.content:
            return PromptKeys.TRANSITION.value
        else:
            return response.choices[0].message.content
