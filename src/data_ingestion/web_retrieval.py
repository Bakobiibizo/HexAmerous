import requests
from bs4 import BeautifulSoup
from typing import Optional
from openai.types.beta.threads import ThreadMessage
from openai.pagination import SyncCursorPage
from utils.ops_api_handler import create_web_retrieval_runstep
from utils.tools import ActionItem
from utils.openai_clients import litellm_client
from data_models import run
import os
from utils.coala import CoALA

class WebRetrieval:
    def __init__(
        self,
        run_id: str,
        thread_id: str,
        assistant_id: str,
        tools_map: dict[str, ActionItem],
        job_summary: str,
    ):
        self.query_maker_instructions = f"""Your role is to generate a search query based on the current working memory and the job summary.
Only respond with the search query itself, NOTHING ELSE."""
        self.run_id = run_id
        self.thread_id = thread_id
        self.assistant_id = assistant_id
        self.tool_items = tools_map
        self.job_summary = job_summary
        self.coala = None

    def generate(
        self,
        messages: SyncCursorPage[ThreadMessage],
        runsteps: SyncCursorPage[run.RunStep],
        content: Optional[str] = None,
    ) -> run.RunStep:
        self.coala = CoALA(
            runsteps=runsteps,
            messages=messages,
            job_summary=self.job_summary,
            tools_map=self.tool_items,
        )

        query = self.generate_search_query()
        print("Web retrieval query:", query)

        search_results = self.perform_web_search(query)
        
        run_step = create_web_retrieval_runstep(
            self.thread_id,
            self.run_id,
            self.assistant_id,
            search_results,
            site="google.com",  # You might want to make this configurable
        )
        return run_step

    def generate_search_query(self) -> str:
        messages = [
            {
                "role": "user",
                "content": self.compose_query_system_prompt(),
            },
        ]
        response = litellm_client.chat.completions.create(
            model=os.getenv("LITELLM_MODEL"),
            messages=messages,
            max_tokens=200,
        )
        return response.choices[0].message.content

    def perform_web_search(self, query: str) -> str:
        # This is a simple implementation. You might want to use a proper search API for production.
        url = f"https://www.google.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract search results
        search_results = []
        for g in soup.find_all('div', class_='g'):
            anchor = g.find('a')
            if anchor:
                link = anchor['href']
                title = anchor.find('h3')
                if title:
                    title = title.text
                    search_results.append(f"{title}\n{link}\n\n")
        
        return "".join(search_results[:5])  # Return top 5 results

    def compose_query_system_prompt(self) -> str:
        trace = self.coala.compose_trace()

        composed_instruction = f"""{self.query_maker_instructions} 

Current working memory:
Question: {self.job_summary}
{trace}"""
        print("\n\nWEB RETRIEVAL SYSTEM PROMPT: ", composed_instruction)
        return composed_instruction