from typing import List
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class FewShotExample:
    seed: str
    post: str
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class Prompt:
    system_content: str
    user_content: str
    id: str 
    name: str
    examples: List[FewShotExample]
    num_predict: int = 200
    temperature: float = 0.75


@dataclass
class Post:
    id: str
    seed: str
    content: str


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
