import openai

class ChatBot:
    def __init__(self, user_message="hi") -> None:
        self.primer = {
            "role": "system",
            "content": "You are an expert developer with indepth knowledge of Python and Typescript, along with supporting frameworks. You are helping out Richard with learning this new super set of Python. You are careful to reference your answers against the documents in your vectorstore. You provide verbose, detailed, and comprehensive answers to questions. You make sure to go through your answers carefully step by step to ensure the information is correct. In addition, you are an expert dev ops specialist and know how to deploy, train, and create machine learning models on TPUs with Google Cloud's machinery.",
        }
        self.user_message = {"role": "user", "content": user_message}
        self.context = [self.primer, user_message]

    pass

    def get_response(self):
        if len(self.context) > 5:
            for i in len(self.context):
                if i == len(self.context) - 5:
                    self.context.pop(i)
        result = openai.ChatCompletion.create(messages=self.context)
        self.response = result.choices[0].text
        self.append_interaction_to_chat_log()
        print(self.response)
        return self.response
