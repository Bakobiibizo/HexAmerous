from pydantic import BaseModel
from loguru import logger
from typing import List, Optional
from src.data_models.generators import TokenizerConfig



input_config = TokenizerConfig(
    

)


class TikTokenizer(Tokenizer):
    
    def __init__(self, input_config: Optional[Tokenizer]=input_config):
        super().__init__(input_config or self.config)
        
    def install_dependencies(self):
        try: 
            import torch
            from transformers import AutoModel, AutoTokenizer
        except Exception as e:
            logger.warn(str(e))
            
    def setup_tokenizer(self):
        try:
            self.device = self.get_device()

            self.model = AutoModel.from_pretrained(
                self.model_path, 
                device_map=self.device
                )
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                device_map=self.device
                )
            self.model = self.model.to(
                self.device
                )
        except Exception as e:
            logger.warn(str(e))
            
    def get_device():
        try:
            if torch.cuda.is_available():
                return torch.device("cuda")
            elif torch.backends.mps.is_available():
                return torch.device("mps")
            else:
                return torch.device("cpu")
        except Exception as e:
            logger.warn(str(e))

    def tokenize(self, chunk) -> List[float]:
        try: 
            return self.tokenizer.tokenize(chunk)
        except Exception as e:
            logger.warn(str(e))

    
    def embed(
        self, 
        tokens=None, 
        ):
        max_length = self.tokenizer.model_max_length
        if len(tokens) > max_length:
            tokens = tokens[:max_length]
        if len(tokens) < max_length:
            tokens = tokens + ["[PAD]"] * (max_length - len(tokens))

        encoded_input = self.tokenizer(
            tokens, 
            padding="max_length", 
            max_length=max_length, 
            truncation=True, 
            return_tensors="pt"
            )
        encoded_input = encoded_input.to(self.device)
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        model_output = model_output.last_hidden_state.squeeze(0)
        return model_output.tolist()


    def vectorize_chunk(self, chunk) -> List[float]:
        try:
            import torch
            tokens = self.tokenize(chunk)
            return self.embed(tokens)
        except Exception as e:
            logger.warn(str(e))