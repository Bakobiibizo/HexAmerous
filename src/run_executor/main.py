from typing import Dict, Any, Optional, List
from constants import PromptKeys
from utils.tools import ActionItem, Actions, tools_to_map
from utils.ops_api_handler import create_message_runstep, update_run
from data_models import run
from openai.types.beta.threads import ThreadMessage
from utils.openai_clients import assistants_client
from openai.types.beta.thread import Thread
from openai.types.beta import Assistant
from openai.pagination import SyncCursorPage
from agents import router, summarizer, orchestrator
from actions import retrieval, text_generation, final_answer, web_retrieval
import datetime

# TODO: add assistant and base tools off of assistant


class ExecuteRun:
    def __init__(self, thread_id: str, run_id: str, run_config: Dict[str, Any] = {}):
        self.run_id = run_id
        self.thread_id = thread_id
        self.assistant_id: Optional[str] = None
        self.run_config = run_config

        self.run: Optional[run.Run] = None
        self.messages: Optional[SyncCursorPage(ThreadMessage)] = None
        self.thread: Optional[Thread] = None
        self.assistant: Optional[Assistant] = None
        self.tools_map: Optional[dict[str, ActionItem]] = None
        self.runsteps: Optional[SyncCursorPage[run.RunStep]] = None
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
        print("Run: ", self.run, "\n\n")

        # Get the thread messages
        # TODO: should only populate these entities once
        thread = assistants_client.beta.threads.retrieve(
            thread_id=self.thread_id,
        )
        self.thread = thread

        assistant = assistants_client.beta.assistants.retrieve(
            assistant_id=self.run.assistant_id,
        )
        self.assistant_id = assistant.id
        self.assistant = assistant
        self.tools_map = tools_to_map(self.assistant.tools)

        messages = assistants_client.beta.threads.messages.list(
            thread_id=self.thread_id, order="asc"
        )
        self.messages = messages
        print("\n\nMain Messages: ", self.messages, "\n\n")

        router_agent = router.RouterAgent()
        router_response = router_agent.generate(self.tools_map, self.messages)
        print("Response: ", router_response, "\n\n")
        if router_response != PromptKeys.TRANSITION.value:
            create_message_runstep(
                self.thread_id, self.run_id, self.run.assistant_id, router_response
            )
            update_run(
                self.thread_id,
                self.run_id,
                run.RunUpdate(status=run.RunStatus.COMPLETED.value),
            )
            print("Generating response")
            print(f"Finished executing run {self.run_id}")
            return
        print("Transitioning")

        summarizer_agent = summarizer.SummarizerAgent()
        summary = summarizer_agent.generate(self.tools_map, self.messages)
        print("\n\nSummary: ", summary, "\n\n")

        orchestrator_agent = orchestrator.OrchestratorAgent(
            self.run_id, self.thread_id, self.tools_map, summary
        )
        orchestrator_response = None
        # handle action or tool
        t_loops = 0
        while (
            orchestrator_response
            not in [
                Actions.COMPLETION,
                Actions.FAILURE,
            ]
            and t_loops < 5
        ):
            t_loops += 1
            # Get updated run state
            messages = assistants_client.beta.threads.messages.list(
                thread_id=self.thread_id, order="asc"
            )
            self.messages = messages
            runsteps = assistants_client.beta.threads.runs.steps.list(
                thread_id=self.thread_id,
                run_id=self.run_id,
                order="asc"
            )
            self.runsteps = runsteps

            # Execute thought
            if len(runsteps.data) == 0 or runsteps.data[0].type == "tool_calls":
                action = text_generation.TextGeneration(
                    self.run_id,
                    self.thread_id,
                    self.assistant_id,
                    self.tools_map,
                    summary,
                )
                action.generate(messages, runsteps)
                continue

            # Execute orchestrator
            orchestrator_response = orchestrator_agent.generate(messages, runsteps)
            print("\n\nOrchestrator Response: ", orchestrator_response, "\n\n")
            if orchestrator_response == Actions.RETRIEVAL:
                action = retrieval.Retrieval(
                    self.run_id,
                    self.thread_id,
                    self.assistant_id,
                    self.tools_map,
                    summary,
                )
                action.generate(messages, runsteps)
                continue
            if orchestrator_response == Actions.WEB_RETREIVAL: # TODO: Sean, entry point for web retrieval
                action = web_retrieval.WebRetrieval(
                    self.run_id,
                    self.thread_id,
                    self.assistant_id,
                    self.tools_map,
                    summary,
                )
                action.generate(messages, runsteps)
                continue
            if orchestrator_response == Actions.COMPLETION:
                action = final_answer.FinalAnswer(
                    self.run_id,
                    self.thread_id,
                    self.assistant_id,
                    self.tools_map,
                    summary,
                )
                action.generate(messages, runsteps)
                run_update = run.RunUpdate(
                    status=run.RunStatus.COMPLETED.value,
                    completed_at=runsteps.data[0].created_at,
                )

                # Call the API handler to update the run status
                updated_run = update_run(self.thread_id, self.run_id, run_update)
                continue
            # retrieve from website
            # 

        print(f"Finished executing run {self.run_id}. Total loops: {t_loops}")

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
