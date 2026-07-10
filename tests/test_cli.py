import json
from pathlib import Path

from hexamerous.cli import main


def test_doctor_and_chat(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("HEXAMEROUS_DATA_DIR", str(tmp_path))
    assert main(["doctor"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["status"] == "ok"
    assert doctor["providers"] == ["echo"]
    assert main(["chat", "hello", "--provider", "echo", "--model", "offline"]) == 0
    assert capsys.readouterr().out.strip() == "Echo: hello"

