# api_handler.py
import requests
from data_models import run
import os
from dotenv import load_dotenv

# TODO: create run script that imports env vars
load_dotenv()
BASE_URL = os.getenv("ASSISTANTS_API_URL")


def update_run(thread_id: str, run_id: str, run: run.RunUpdate) -> bool:
    """
    Update the status of a Run.

    Parameters:
    thread_id (str): The ID of the thread.
    run_id (str): The ID of the run.
    new_status (str): The new status to set for the run.

    Returns:
    bool: True if the status was successfully updated, False otherwise.
    """
    update_url = f"{BASE_URL}/ops/threads/{thread_id}/runs/{run_id}"
    update_data = run.model_dump(exclude_none=True)
    print(f"Data to update: {update_data}")

    response = requests.post(update_url, json=update_data)

    if response.status_code == 200:
        return True
    else:
        # You can also log the error or throw an exception here depending on how you want to handle errors.
        return False


# You can add more API functions as
