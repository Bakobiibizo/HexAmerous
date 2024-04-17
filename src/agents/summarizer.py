from openai.types.beta.threads import Message
from openai.pagination import SyncCursorPage
from utils.openai_clients import litellm_client


class SummarizerAgent:
    def __init__(self):
        self.role_instructions = """Your role is to utilize all messages and additional provided information to produce a concise summarization.
This summarization should contain sufficient information to fulfill the current request.
Also take the tools available to you into consideration as they will be used to fulfill the request."""

    def generate(self, tools: dict, paginated_messages: SyncCursorPage[Message]) -> str:
        """
        Create a summary of the chat history with an emphasis on the current user request and tool use.

        Args:
            tools (dict): A dictionary containing available tools and their descriptions.
            chat_history (list): A list of messages representing the chat history.

        Returns:
            str: A summary useful for planning and tool use.
        """
        # Compose the prompt for the summarization task
        system_prompt = self.compose_system_prompt(tools)

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]
        for message in paginated_messages.data:
            messages.append(
                {
                    "role": message.role,
                    "content": message.content[0].text.value,
                }
            )

        # Call to the AI model to generate the summary
        response = litellm_client.chat.completions.create(
            model="mixtral",  # Replace with your model of choice
            messages=messages,
            max_tokens=1000,  # You may adjust the token limit as necessary
        )

        # Extract the summary from the response
        summary = response.choices[0].message.content
        return summary

    def compose_system_prompt(self, tools: dict) -> str:
        tools_list = "\n".join(
            [f"- {name}: {config['description']}" for name, config in tools.items()]
        )
        return f"""{self.role_instructions}

The tools available to you are:
{tools_list}"""
