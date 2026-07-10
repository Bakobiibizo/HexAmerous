from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

from .models import Message


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    model: str
    system_prompt: str
    messages: Sequence[Message]
    context: str = ""


class Provider(Protocol):
    name: str

    def stream(self, request: GenerationRequest) -> Iterable[str]: ...


class EchoProvider:
    """Deterministic offline provider used by diagnostics and tests."""

    name = "echo"

    def stream(self, request: GenerationRequest) -> Iterable[str]:
        user_messages = [item.content for item in request.messages if item.role.value == "user"]
        response = user_messages[-1] if user_messages else ""
        yield f"Echo: {response}"


class OpenAIProvider:
    name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("Install HexAmerous with the 'openai' extra") from error
        self.client = OpenAI(api_key=api_key)

    def stream(self, request: GenerationRequest) -> Iterable[str]:
        messages = [{"role": "system", "content": request.system_prompt}]
        if request.context:
            messages.append({"role": "system", "content": request.context})
        messages.extend(
            {"role": item.role.value, "content": item.content} for item in request.messages
        )
        response = self.client.chat.completions.create(
            model=request.model, messages=messages, stream=True
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str | None = None) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as error:
            raise RuntimeError("Install HexAmerous with the 'anthropic' extra") from error
        self.client = Anthropic(api_key=api_key)

    def stream(self, request: GenerationRequest) -> Iterable[str]:
        system = request.system_prompt
        if request.context:
            system = f"{system}\n\n{request.context}"
        messages = [
            {"role": item.role.value, "content": item.content}
            for item in request.messages
            if item.role.value != "system"
        ]
        with self.client.messages.stream(
            model=request.model, max_tokens=4096, system=system, messages=messages
        ) as stream:
            yield from stream.text_stream


def configured_providers() -> list[Provider]:
    providers: list[Provider] = [EchoProvider()]
    if os.getenv("OPENAI_API_KEY"):
        providers.append(OpenAIProvider())
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append(AnthropicProvider())
    return providers
