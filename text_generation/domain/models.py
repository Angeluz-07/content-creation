from dataclasses import dataclass

@dataclass
class Prompt:
    system_content: str
    user_content: str
    id: str 
    name: str
    num_predict: int = 200

@dataclass
class Post:
    id: str
    seed: str
    content: str