import json
import subprocess
from pathlib import Path

import pytest

from hexamerous.config import Settings
from hexamerous.ingestion import GristIndexer
from hexamerous.models import Role
from hexamerous.service import AgentService
from hexamerous.storage import Repository


@pytest.fixture
def service(tmp_path: Path) -> AgentService:
    settings = Settings(tmp_path, tmp_path / "hex.sqlite3", "echo", "offline")
    return AgentService(settings)


def test_conversation_round_trip(service: AgentService) -> None:
    conversation = service.new_conversation("First chat")
    assert service.send(conversation.id, "write a parser") == "Echo: write a parser"
    messages = service.repository.messages(conversation.id)
    assert [message.role for message in messages] == [Role.USER, Role.ASSISTANT]
    assert [message.sequence for message in messages] == [0, 1]


def test_unknown_provider_does_not_persist_assistant_message(service: AgentService) -> None:
    conversation = service.new_conversation("Missing", provider="missing")
    with pytest.raises(ValueError, match="not configured"):
        service.send(conversation.id, "hello")
    assert [message.role for message in service.repository.messages(conversation.id)] == [Role.USER]


def test_workspace_index_and_search(service: AgentService, tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    workspace = service.repository.create_workspace("Example", root)
    envelope = {
        "schema_version": "grist/envelope/v1",
        "kind": "repo_ingest",
        "payload": {"artifacts": [{
            "path": "parser.py", "kind": "python_code", "content_hash": "sha256:test",
            "artifact": {"payload": {"symbols": [{"name": "parse_invoice"}]}}
        }]},
    }
    def runner(command):
        assert command == ["grist", "ingest", "repo", str(root.resolve())]
        return subprocess.CompletedProcess(command, 0, json.dumps(envelope), "")
    assert GristIndexer(service.repository, runner).index(workspace.id, root) == 1
    results = service.repository.search(workspace.id, "parse invoice")
    assert results[0].relative_path == "parser.py"
    assert "[parse]_[invoice]" in results[0].snippet


def test_grist_schema_is_validated(service: AgentService, tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    workspace = service.repository.create_workspace("Example", root)
    def runner(command):
        return subprocess.CompletedProcess(command, 0, '{"schema_version":"wrong"}', "")
    with pytest.raises(RuntimeError, match="Unsupported Grist"):
        GristIndexer(service.repository, runner).index(workspace.id, root)


def test_foreign_keys_and_cascade(tmp_path: Path) -> None:
    repository = Repository(tmp_path / "db.sqlite3")
    repository.migrate()
    conversation = repository.create_conversation("Delete me", "echo", "offline", "system")
    repository.add_message(conversation.id, Role.USER, "message")
    with repository.connect() as db:
        db.execute("DELETE FROM conversations WHERE id = ?", (conversation.id,))
    assert repository.messages(conversation.id) == []


def test_migration_is_idempotent(service: AgentService) -> None:
    service.repository.migrate()
    service.repository.migrate()
