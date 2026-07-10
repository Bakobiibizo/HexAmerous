from __future__ import annotations

from collections.abc import Callable, Iterable

from .config import Settings
from .models import Conversation, Role
from .providers import EchoProvider, GenerationRequest, Provider
from .storage import Repository


class AgentService:
    def __init__(
        self,
        settings: Settings,
        repository: Repository | None = None,
        providers: Iterable[Provider] = (),
    ) -> None:
        self.settings = settings
        self.repository = repository or Repository(settings.database_path)
        self.repository.migrate()
        self.providers = {provider.name: provider for provider in providers}
        self.providers.setdefault("echo", EchoProvider())

    def new_conversation(
        self,
        title: str,
        provider: str | None = None,
        model: str | None = None,
        workspace_id: str | None = None,
        system_prompt: str = "You are HexAmerous, a precise senior software engineering agent.",
    ) -> Conversation:
        return self.repository.create_conversation(
            title,
            provider or self.settings.default_provider,
            model or self.settings.default_model,
            system_prompt,
            workspace_id,
        )

    def send(
        self,
        conversation_id: str,
        content: str,
        on_token: Callable[[str], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> str:
        conversation = self.repository.get_conversation(conversation_id)
        self.repository.add_message(conversation_id, Role.USER, content)
        messages = self.repository.messages(conversation_id)
        context = self._context(conversation, content)
        try:
            provider = self.providers[conversation.provider]
        except KeyError as error:
            raise ValueError(f"Provider is not configured: {conversation.provider}") from error
        chunks: list[str] = []
        for token in provider.stream(
            GenerationRequest(
                model=conversation.model,
                system_prompt=conversation.system_prompt,
                messages=messages,
                context=context,
            )
        ):
            if cancelled and cancelled():
                raise InterruptedError("Generation cancelled")
            chunks.append(token)
            if on_token:
                on_token(token)
        response = "".join(chunks).strip()
        if not response:
            raise RuntimeError("Provider returned an empty response")
        self.repository.add_message(conversation_id, Role.ASSISTANT, response)
        return response

    def _context(self, conversation: Conversation, query: str) -> str:
        if conversation.workspace_id is None:
            return ""
        results = self.repository.search(
            conversation.workspace_id, query, self.settings.context_results
        )
        blocks: list[str] = []
        size = 0
        for result in results:
            block = f"File: {result.relative_path}\n{result.snippet}"
            if size + len(block) > self.settings.context_character_limit:
                break
            blocks.append(block)
            size += len(block)
        return "Relevant workspace context:\n\n" + "\n\n".join(blocks) if blocks else ""
