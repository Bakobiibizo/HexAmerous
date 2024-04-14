import random
from openai.types.beta.threads import Message
from openai.pagination import SyncCursorPage
from tools.openai_clients import litellm_client




class RouterAgent:
    def __init__(
        self,
    ):
        self.role = f"""Your role is to determine whether to use tools or directly generate a response.
In the case that you need to use tools, simply respond with '<TRANSITION>'. Otherwise, generate an appropriate response.

The tools available to you are:"""

    def compose_system_prompt(self, tools: dict) -> str:
        tools_list = ""
        for idx, (tool_name, tool_config) in enumerate(tools.items()):
            tools_list += f"{idx + 1}. {tool_name}: {tool_config['description']}\n"
        return f"""{self.role}

The tools available to you are:
{tools_list}"""

    # TODO: add assistant and base tools off of assistant
    def generate(
        self, tools: dict, paginated_messages: SyncCursorPage[Message]
    ) -> str:
        """
        Generates a response based on the chat history and role instructions.

        Args:
            tools (dict): The tools available to the agent.
            paginated_messages (SyncCursorPage[Message]): The chat history.

        Returns:
            str: It either returns `<TRANSITION>` or a generated response.
        """

        messages = [
            {
                "role": "system",
                "content": self.compose_system_prompt(tools),
            }
        ]
        for message in paginated_messages.data:
            messages.append(
                {
                    "role": message.role,
                    "content": message.content[0].text.value,
                }
            )
        print("MESSAGES: ", messages)
        response = litellm_client.chat.completions.create(
            model="mixtral",
            messages=messages,
            max_tokens=500,
        )

        print("GENERATION: ", response.choices[0].message.content)
        if "<TRANSITION>" in response.choices[0].message.content:
            return "<TRANSITION>"
        else:
            return response.choices[0].message.content


