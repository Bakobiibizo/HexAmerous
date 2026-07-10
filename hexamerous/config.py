from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from platformdirs import user_config_path, user_data_path


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    database_path: Path
    default_provider: str = "openai"
    default_model: str = "gpt-4o-mini"
    context_results: int = 6
    context_character_limit: int = 24_000

    @classmethod
    def load(cls, config_path: Path | None = None) -> Settings:
        data_dir = Path(os.getenv("HEXAMEROUS_DATA_DIR", user_data_path("HexAmerous")))
        values: dict[str, object] = {}
        path = config_path or Path(
            os.getenv("HEXAMEROUS_CONFIG", user_config_path("HexAmerous") / "config.json")
        )
        if path.exists():
            with path.open(encoding="utf-8") as handle:
                loaded = json.load(handle)
            if not isinstance(loaded, dict):
                raise ValueError("HexAmerous config must contain a JSON object")
            values.update(loaded)
        configured_data = Path(str(values.get("data_dir", data_dir))).expanduser()
        database = Path(
            str(values.get("database_path", configured_data / "hexamerous.sqlite3"))
        ).expanduser()
        return cls(
            data_dir=configured_data,
            database_path=database,
            default_provider=str(values.get("default_provider", "openai")),
            default_model=str(values.get("default_model", "gpt-4o-mini")),
            context_results=int(values.get("context_results", 6)),
            context_character_limit=int(values.get("context_character_limit", 24_000)),
        )

    def save(self, config_path: Path | None = None) -> Path:
        path = config_path or user_config_path("HexAmerous") / "config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(self)
        payload["data_dir"] = str(self.data_dir)
        payload["database_path"] = str(self.database_path)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path
