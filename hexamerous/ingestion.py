from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from uuid import uuid4

from .models import ContextDocument
from .storage import Repository, utc_now

CommandRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def _run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True)


class GristIndexer:
    """Imports Grist's semantic repository envelope into local full-text search."""

    def __init__(self, repository: Repository, runner: CommandRunner = _run) -> None:
        self.repository = repository
        self.runner = runner

    def index(self, workspace_id: str, root: Path) -> int:
        root = root.resolve()
        if not root.is_dir():
            raise ValueError(f"Workspace root is not a directory: {root}")
        if self.runner is _run and shutil.which("grist") is None:
            raise RuntimeError("Grist is required for workspace indexing; install the grist CLI")
        try:
            completed = self.runner(["grist", "ingest", "repo", str(root)])
        except subprocess.CalledProcessError as error:
            detail = error.stderr.strip() or str(error)
            raise RuntimeError(f"Grist ingestion failed: {detail}") from error
        try:
            envelope = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError("Grist returned invalid JSON") from error
        if (
            envelope.get("schema_version") != "grist/envelope/v1"
            or envelope.get("kind") != "repo_ingest"
            or not isinstance(envelope.get("payload"), dict)
        ):
            raise RuntimeError("Unsupported Grist repository envelope")
        payload = envelope["payload"]
        artifacts = payload.get("artifacts")
        if not isinstance(artifacts, list):
            raise RuntimeError("Grist envelope is missing artifacts")
        documents: list[ContextDocument] = []
        for item in artifacts:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                continue
            artifact = item.get("artifact")
            if not isinstance(artifact, dict):
                continue
            content_hash = str(item.get("content_hash", ""))
            documents.append(
                ContextDocument(
                    id=str(uuid4()),
                    workspace_id=workspace_id,
                    relative_path=item["path"],
                    content=json.dumps(artifact, sort_keys=True, separators=(",", ":")),
                    content_hash=content_hash,
                    language=str(item.get("kind", "unknown")),
                    updated_at=utc_now(),
                )
            )
        return self.repository.reconcile_documents(workspace_id, documents)
