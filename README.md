# HexAmorous: Run Executor Worker
This serves as the run executor to [OpenGPTs-platform](https://github.com/OpenGPTs-platform).


To elaborate, when you create an assistant with the `assistants-api`, then set up a thread and use a `run` command like
```py
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)
```
This will create a `run` object that will be sent to the `RabbitMQ` queue. Then this repository, that is already listening to the queue, will consume the request and execute the `run` by generating text and using tools in a loop until the user’s message has been adequately responded to.
## Quickstart
0. If you intend to use a custom version of `assistants-api` we recommend you use  [OpenGPTs-platform/assistants-api](https://github.com/OpenGPTs-platform/assistants-api) follow the [quickstart guide](https://github.com/OpenGPTs-platform/assistants-api?tab=readme-ov-file#quickstart) to get the API running. Alternatively you can use the official OpenAI Assistants's API through `openai==1.13.4`, but you will have limited tool functionality.
1. Copy the [`.env.example`](.env.example) file to `.env` and fill in the required fields.
2. (Recommended: Create a virtual environment) Install the dependencies using `pip install -r requirements.txt`.
3. Run the run executor worker using `python run_executor_worker.py`. This will consume the [`RabbitMQ`](https://www.rabbitmq.com/docs) queue and execute the tasks.