from queue import Queue

class Message:
    def __init__(self, role, text):
        self.role = role
        self.content = text

class Prompt:
    def __init__(self, role, text, prompt_messages=None):
        if prompt_messages is None:
            prompt_messages = Queue(maxsize=8)
        self.role = role
        self.text = text
        self.prompt_messages = prompt_messages

    def to_messages(self):
        messages = []
        while not self.prompt_messages.empty():
            message = Message(role=self.role, text=self.prompt_messages.get())
            messages.append(message)
        return messages

    def set_prompts(self, prompts):
        for prompt in prompts:
            role = next(iter(prompt.keys()))
            text = next(iter(prompt.values()))
            self.prompt_messages.put(text)
            if self.prompt_messages.qsize() > 8:
                self.prompt_messages.get(block=False)
        return self.to_messages()

    def append(self, message):
        self.prompt_messages.put(message.text)
        if self.prompt_messages.qsize() > 8:
            self.prompt_messages.get(block=False)
        return self.to_messages()


    def __iter__(self):
        return iter(self.to_messages())