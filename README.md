# HexAmerous

HexAmerous is a local-first command-line coding agent. It keeps conversations and
project context in a local SQLite database, uses [Grist](https://github.com/hydra-dynamix)
for explicit repository ingestion, and connects to model providers through small,
optional adapters.

HexAmerous does not require a hosted vector database, message broker, or background
service. Nothing is indexed until you run the workspace command.

## Requirements

- Python 3.11 or newer
- `grist` on `PATH` when indexing repositories
- An API key only when using a hosted model provider

## Install

```bash
uv tool install .
```

For development:

```bash
uv sync --extra dev
uv run pytest
```

Provider SDKs are optional:

```bash
uv sync --extra openai
uv sync --extra anthropic
```

## Commands

Validate the local database and list configured providers:

```bash
hexamerous doctor
```

Create a workspace and ingest its semantic structure through Grist:

```bash
hexamerous workspace ~/repos/my-project --name my-project
```

Run an offline diagnostic conversation:

```bash
hexamerous chat "check the local conversation store" --provider echo --model offline
```

List persisted conversations:

```bash
hexamerous list
```

Application state uses the platform data directory by default. Override it with
`HEXAMEROUS_DATA_DIR`; set `HEXAMEROUS_CONFIG` to load a different JSON config.

## Privacy

Conversation history, workspace metadata, and imported Grist artifacts are stored
locally. Content sent to a hosted model is subject to that provider's policies.
HexAmerous never reads or indexes a repository implicitly.

## Status

The local core, migrations, Grist ingestion boundary, provider protocol, and CLI
are covered by isolated tests. OpenAI and Anthropic adapters are optional so the
core remains usable and testable without credentials or network access.
