from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class Workspace:
    id: str
    name: str
    root_path: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class Conversation:
    id: str
    workspace_id: str | None
    title: str
    provider: str
    model: str
    system_prompt: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class Message:
    id: str
    conversation_id: str
    role: Role
    content: str
    created_at: str
    sequence: int


@dataclass(frozen=True, slots=True)
class ContextDocument:
    id: str
    workspace_id: str
    relative_path: str
    content: str
    content_hash: str
    language: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class SearchResult:
    relative_path: str
    snippet: str
    rank: float
