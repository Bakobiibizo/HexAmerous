from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .models import ContextDocument, Conversation, Message, Role, SearchResult, Workspace

SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class Repository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def migrate(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_info (
                    version INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS workspaces (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    root_path TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT REFERENCES workspaces(id) ON DELETE SET NULL,
                    title TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    system_prompt TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    UNIQUE(conversation_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
                    relative_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    language TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(workspace_id, relative_path)
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    relative_path, content, content='documents', content_rowid='rowid'
                );
                CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                    INSERT INTO documents_fts(rowid, relative_path, content)
                    VALUES (new.rowid, new.relative_path, new.content);
                END;
                CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, relative_path, content)
                    VALUES ('delete', old.rowid, old.relative_path, old.content);
                END;
                CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, relative_path, content)
                    VALUES ('delete', old.rowid, old.relative_path, old.content);
                    INSERT INTO documents_fts(rowid, relative_path, content)
                    VALUES (new.rowid, new.relative_path, new.content);
                END;
                """
            )
            current = db.execute("SELECT version FROM schema_info LIMIT 1").fetchone()
            if current is None:
                db.execute("INSERT INTO schema_info(version) VALUES (?)", (SCHEMA_VERSION,))
            elif current["version"] != SCHEMA_VERSION:
                raise RuntimeError(f"Unsupported database schema {current['version']}")

    def create_workspace(self, name: str, root_path: Path) -> Workspace:
        now = utc_now()
        workspace = Workspace(str(uuid4()), name.strip(), str(root_path.resolve()), now, now)
        if not workspace.name:
            raise ValueError("Workspace name cannot be empty")
        with self.connect() as db:
            db.execute(
                "INSERT INTO workspaces VALUES (?, ?, ?, ?, ?)",
                (workspace.id, workspace.name, workspace.root_path, now, now),
            )
        return workspace

    def list_workspaces(self) -> list[Workspace]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM workspaces ORDER BY updated_at DESC").fetchall()
        return [Workspace(**dict(row)) for row in rows]

    def find_workspace(self, root_path: Path) -> Workspace | None:
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM workspaces WHERE root_path = ?", (str(root_path.resolve()),)
            ).fetchone()
        return Workspace(**dict(row)) if row else None

    def delete_workspace(self, workspace_id: str) -> bool:
        with self.connect() as db:
            result = db.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
        return result.rowcount > 0

    def create_conversation(
        self,
        title: str,
        provider: str,
        model: str,
        system_prompt: str,
        workspace_id: str | None = None,
    ) -> Conversation:
        now = utc_now()
        conversation = Conversation(
            str(uuid4()),
            workspace_id,
            title.strip() or "New conversation",
            provider,
            model,
            system_prompt,
            now,
            now,
        )
        with self.connect() as db:
            db.execute(
                "INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                tuple(conversation.__dict__.values())
                if hasattr(conversation, "__dict__")
                else (
                    conversation.id,
                    conversation.workspace_id,
                    conversation.title,
                    conversation.provider,
                    conversation.model,
                    conversation.system_prompt,
                    conversation.created_at,
                    conversation.updated_at,
                ),
            )
        return conversation

    def get_conversation(self, conversation_id: str) -> Conversation:
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Conversation not found: {conversation_id}")
        return Conversation(**dict(row))

    def list_conversations(self, workspace_id: str | None = None) -> list[Conversation]:
        query = "SELECT * FROM conversations"
        params: tuple[str, ...] = ()
        if workspace_id is not None:
            query += " WHERE workspace_id = ?"
            params = (workspace_id,)
        query += " ORDER BY updated_at DESC"
        with self.connect() as db:
            rows = db.execute(query, params).fetchall()
        return [Conversation(**dict(row)) for row in rows]

    def delete_conversation(self, conversation_id: str) -> bool:
        with self.connect() as db:
            result = db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        return result.rowcount > 0

    def add_message(self, conversation_id: str, role: Role, content: str) -> Message:
        if not content.strip():
            raise ValueError("Message content cannot be empty")
        with self.connect() as db:
            sequence = db.execute(
                "SELECT COALESCE(MAX(sequence), -1) + 1 FROM messages WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()[0]
            message = Message(str(uuid4()), conversation_id, role, content, utc_now(), sequence)
            db.execute(
                "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)",
                (message.id, conversation_id, role.value, content, message.created_at, sequence),
            )
            db.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (message.created_at, conversation_id),
            )
        return message

    def messages(self, conversation_id: str) -> list[Message]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY sequence",
                (conversation_id,),
            ).fetchall()
        return [Message(**{**dict(row), "role": Role(row["role"])}) for row in rows]

    def upsert_documents(self, documents: Sequence[ContextDocument]) -> int:
        if not documents:
            return 0
        with self.connect() as db:
            db.executemany(
                """INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspace_id, relative_path) DO UPDATE SET
                    content=excluded.content, content_hash=excluded.content_hash,
                    language=excluded.language, updated_at=excluded.updated_at""",
                [
                    (
                        item.id,
                        item.workspace_id,
                        item.relative_path,
                        item.content,
                        item.content_hash,
                        item.language,
                        item.updated_at,
                    )
                    for item in documents
                ],
            )
        return len(documents)

    def reconcile_documents(self, workspace_id: str, documents: Sequence[ContextDocument]) -> int:
        paths = {item.relative_path for item in documents}
        self.upsert_documents(documents)
        with self.connect() as db:
            rows = db.execute(
                "SELECT relative_path FROM documents WHERE workspace_id = ?", (workspace_id,)
            ).fetchall()
            stale = [row["relative_path"] for row in rows if row["relative_path"] not in paths]
            db.executemany(
                "DELETE FROM documents WHERE workspace_id = ? AND relative_path = ?",
                [(workspace_id, path) for path in stale],
            )
        return len(documents)

    def search(self, workspace_id: str, query: str, limit: int = 6) -> list[SearchResult]:
        terms = " ".join(part for part in query.replace('"', " ").split() if len(part) > 1)
        if not terms:
            return []
        with self.connect() as db:
            rows = db.execute(
                """SELECT d.relative_path,
                    snippet(documents_fts, 1, '[', ']', '...', 24) AS snippet,
                    bm25(documents_fts) AS rank
                FROM documents_fts
                JOIN documents d ON d.rowid = documents_fts.rowid
                WHERE documents_fts MATCH ? AND d.workspace_id = ?
                ORDER BY rank LIMIT ?""",
                (terms, workspace_id, limit),
            ).fetchall()
        return [SearchResult(**dict(row)) for row in rows]
