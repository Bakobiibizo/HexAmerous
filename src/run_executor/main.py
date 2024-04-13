from typing import Dict, Any, Optional
from tools.ops_api_handler import update_run
from data_models import run


class ExecuteRun:
    def __init__(self, thread_id: str, run_id: str, run_config: Dict[str, Any] = {}):
        self.run_id = run_id
        self.thread_id = thread_id
        self.run_config = run_config

        self.run: Optional[run.Run] = None
        self.thread = None

    def execute(self):
        # Create an instance of the RunUpdate schema with the new status
        run_update = run.RunUpdate(status=run.RunStatus.IN_PROGRESS.value)

        # Call the API handler to update the run status
        updated_run = update_run(self.thread_id, self.run_id, run_update)

        if not updated_run:
            print(f"Error updating run status for {self.run_id}. Aborting execution.")
            return

        self.run = updated_run

        print(f"Executing run {self.run_id}")

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
