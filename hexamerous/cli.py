from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import Settings
from .ingestion import GristIndexer
from .providers import configured_providers
from .service import AgentService


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="hexamerous", description="Local-first coding agent")
    root.add_argument("--config", type=Path, help="Path to config.json")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Validate local configuration and database")
    workspace = commands.add_parser("workspace", help="Create and index a workspace")
    workspace.add_argument("path", type=Path)
    workspace.add_argument("--name")
    listing = commands.add_parser("list", help="List conversations")
    listing.add_argument("--workspace")
    chat = commands.add_parser("chat", help="Send one message and persist the conversation")
    chat.add_argument("message")
    chat.add_argument("--conversation")
    chat.add_argument("--provider")
    chat.add_argument("--model")
    show = commands.add_parser("show", help="Show a conversation and its messages")
    show.add_argument("conversation")
    delete = commands.add_parser("delete", help="Delete a conversation")
    delete.add_argument("conversation")
    search = commands.add_parser("search", help="Search indexed Grist artifacts")
    search.add_argument("workspace")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=6)
    remove = commands.add_parser("workspace-remove", help="Remove local workspace context")
    remove.add_argument("workspace")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    settings = Settings.load(args.config)
    service = AgentService(settings, providers=configured_providers())
    if args.command == "doctor":
        print(
            json.dumps(
                {
                    "status": "ok",
                    "database": str(settings.database_path),
                    "providers": sorted(service.providers),
                }
            )
        )
        return 0
    if args.command == "workspace":
        workspace = service.repository.find_workspace(args.path)
        if workspace is None:
            workspace = service.repository.create_workspace(args.name or args.path.name, args.path)
        count = GristIndexer(service.repository).index(workspace.id, args.path)
        print(json.dumps({"id": workspace.id, "name": workspace.name, "documents": count}))
        return 0
    if args.command == "list":
        values = service.repository.list_conversations(args.workspace)
        print(json.dumps([{"id": item.id, "title": item.title} for item in values]))
        return 0
    if args.command == "chat":
        conversation_id = args.conversation
        if conversation_id is None:
            conversation_id = service.new_conversation(
                args.message[:60], args.provider, args.model
            ).id
        print(service.send(conversation_id, args.message))
        return 0
    if args.command == "show":
        conversation = service.repository.get_conversation(args.conversation)
        messages = service.repository.messages(args.conversation)
        print(
            json.dumps(
                {
                    "conversation": {
                        "id": conversation.id,
                        "title": conversation.title,
                        "provider": conversation.provider,
                        "model": conversation.model,
                        "workspace_id": conversation.workspace_id,
                    },
                    "messages": [
                        {
                            "role": item.role.value,
                            "content": item.content,
                            "created_at": item.created_at,
                        }
                        for item in messages
                    ],
                }
            )
        )
        return 0
    if args.command == "delete":
        if not service.repository.delete_conversation(args.conversation):
            raise SystemExit(f"Conversation not found: {args.conversation}")
        return 0
    if args.command == "search":
        results = service.repository.search(args.workspace, args.query, args.limit)
        print(
            json.dumps(
                [
                    {"path": item.relative_path, "snippet": item.snippet, "rank": item.rank}
                    for item in results
                ]
            )
        )
        return 0
    if args.command == "workspace-remove":
        if not service.repository.delete_workspace(args.workspace):
            raise SystemExit(f"Workspace not found: {args.workspace}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
