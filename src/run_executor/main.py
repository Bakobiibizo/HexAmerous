from typing import Dict, Any


class ExecuteRun:
    def __init__(self, run_id: str, run_config: Dict[str, Any] = {}):
        self.run_id = run_id
        self.run_config = run_config

    def execute(self):
        print(f"Executing run {self.run_id}")
        pass

    def get_run_id(self) -> str:
        return self.run_id

    def get_run_config(self) -> Dict[str, Any]:
        return self.run_config

    def get_run_state(self) -> str:
        return "RUNNING"

    def get_run_logs(self) -> str:
        return "Logs for run"

    def get_run_result(self) -> Dict[str, Any]:
        return {"result": "result"}

    def get_run_artifacts(self) -> Dict[str, Any]:
        return {"artifacts": "artifacts"}
