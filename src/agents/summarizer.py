from openai.types.beta.threads import ThreadMessage
from openai.pagination import SyncCursorPage
from utils.tools import ActionItem
from utils.openai_clients import litellm_client
import os


class SummarizerAgent:
    def __init__(self):
        pass

    def generate(
        self,
        tools: dict[str, ActionItem],
        paginated_messages: SyncCursorPage[ThreadMessage],
    ) -> str:
        """
        Create a summary of the chat history with an emphasis on the current user request and tool use.

        Args:
            tools (dict): A dictionary containing available tools and their descriptions.
            chat_history (list): A list of messages representing the chat history.

        Returns:
            str: A summary useful for planning and tool use.
        """
        messages = []
        for message in paginated_messages.data:
            messages.append(
                {
                    "role": message.role,
                    "content": message.content[0].text.value,
                }
            )

        # pass the content of the last message to the compose_prompt method and replace the latest_message variable with the content of the last message
        latest_message = messages[-1]["content"]
        modified_prompt = self.compose_prompt(tools, latest_message)
        messages[-1]["content"] = modified_prompt

        # Call to the AI model to generate the summary
        response = litellm_client.chat.completions.create(
            model=os.getenv("LITELLM_MODEL"),
            messages=messages,
            max_tokens=1000,  # You may adjust the token limit as necessary
        )

        # Extract the summary from the response
        summary = response.choices[0].message.content
        return summary

    def compose_prompt(self, tools: dict[str, ActionItem], latest_message: str) -> str:
        tools_list = "\n".join(
            [f"- {tool.type}: {tool.description}" for _, tool in tools.items()]
        )
        return f"""Summarize the purpose of the message <<{latest_message}>> into a single comprehensive statement.
Ensure that the summary includes all relevant details needed for effective use of the following tools:
{tools_list}"""
