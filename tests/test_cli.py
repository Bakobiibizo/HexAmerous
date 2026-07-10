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


def test_show_list_resume_and_delete(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("HEXAMEROUS_DATA_DIR", str(tmp_path))
    assert main(["chat", "first", "--provider", "echo", "--model", "offline"]) == 0
    capsys.readouterr()
    assert main(["list"]) == 0
    conversation_id = json.loads(capsys.readouterr().out)[0]["id"]
    assert main(["chat", "second", "--conversation", conversation_id]) == 0
    capsys.readouterr()
    assert main(["show", conversation_id]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert [item["content"] for item in shown["messages"]] == [
        "first",
        "Echo: first",
        "second",
        "Echo: second",
    ]
    assert main(["delete", conversation_id]) == 0
    assert main(["list"]) == 0
    assert json.loads(capsys.readouterr().out) == []
