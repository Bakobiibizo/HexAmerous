
from pydantic import BaseModel
from src.data_models.generators import OAIMessage, OAIResponse, OAIRequest
from uuid import uuid4
from datetime import datetime
from src.embeddings.TikTokenizer import TikTokenizer

class Converter(BaseModel):
    prompt: str
    human_template: str
    ai_template: str
    prompt_map: Dict[str, str]



class PromptConverter(Converter):
    def __init__(self, input_config: Optional[Converter]):
        super().__init__(input_config or self.config)
        self.tokenizer = TikTokenizer()

    def get_message_usage(self, message: OAIMessage) -> Dict[str, int]:
        

    def to_OAIResponse(self, messages: List[OAIMessage], model: str) -> OAIResponse:
        for message in messages:
            OAIResponse(
                id=uuid4().hex,
                object="text_completion",
                created=datetime.now().timestamp(),
                model=model,
                choices=choices[
                    {
                        "index": 0,
                        "message":{
                            "role": message.role,
                            "content": message.content
                        },
                        "longprobs": None,
                        "finish_reason": None
                    }
                ],
                usage=
            )