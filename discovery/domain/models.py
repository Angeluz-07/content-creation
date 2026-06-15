from typing import List
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Prompt:
    system_content: str
    user_content: str
    id: str 
    name: str
    num_predict: int = 200
    temperature: float = 0.75
