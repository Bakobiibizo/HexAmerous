from typing import Dict, Any, Optional, List
from tools.ops_api_handler import update_run
from data_models import run
from openai.types.beta.threads import Message
from tools.openai_clients import assistants_client
from openai.types.beta.thread import Thread
from agents import router, summarizer

# TODO: add assistant and base tools off of assistant
tools_config = {
    "text_generation": {
        "description": "general text response",
    },
    "key_retrieval": {
        "description": "a database that contains my private keys",
    },
}

class ExecuteRun:
    def __init__(self, thread_id: str, run_id: str, run_config: Dict[str, Any] = {}):
        self.run_id = run_id
        self.thread_id = thread_id
        self.run_config = run_config

        self.run: Optional[run.Run] = None
        self.messages: Optional[List(Message)] = None
        self.thread: Optional[Thread] = None
        # TODO: add assistant and base tools off of assistant

    def execute(self):
        # Create an instance of the RunUpdate schema with the new status
        run_update = run.RunUpdate(status=run.RunStatus.IN_PROGRESS.value)

        # Call the API handler to update the run status
        updated_run = update_run(self.thread_id, self.run_id, run_update)

        if not updated_run:
            print(f"Error updating run status for {self.run_id}. Aborting execution.")
            return

        self.run = updated_run

        # Get the thread messages
        thread = assistants_client.beta.threads.retrieve(
            thread_id=self.thread_id,
        )
        self.thread = thread

        messages = assistants_client.beta.threads.messages.list(
            thread_id=self.thread_id,
        )
        self.messages = messages

        router_agent = router.RouterAgent()
        router_response = router_agent.generate(tools_config, self.messages)
        print("Response: ", router_response, "\n\n")
        if router_response != "<TRANSITION>":
            # execute completion here
            print("Generating response")
        print("Transitioning")

        summarizer_agent = summarizer.SummarizerAgent()
        summary = summarizer_agent.generate(tools_config, self.messages)
        print("Summary: ", summary, "\n\n")





        print(f"Finished executing run {self.run_id}")

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
