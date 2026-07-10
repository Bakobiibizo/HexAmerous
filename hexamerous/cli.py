from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import Settings
from .ingestion import GristIndexer
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
    chat.add_argument("--provider", default="echo")
    chat.add_argument("--model", default="offline")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    settings = Settings.load(args.config)
    service = AgentService(settings)
    if args.command == "doctor":
        print(json.dumps({
            "status": "ok", "database": str(settings.database_path),
            "providers": sorted(service.providers),
        }))
        return 0
    if args.command == "workspace":
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
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
