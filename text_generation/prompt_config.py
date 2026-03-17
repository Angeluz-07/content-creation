from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import json
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_CONFIG_PATH = BASE_DIR / ".data" / ".prompts_config.json"

@dataclass
class PromptConfig:
    system_content: str
    user_content: str
    id: str 
    name: str
    num_predict: int = 200


class PromptConfigRepo:
    def __init__(self, file_path: str = PROMPT_CONFIG_PATH):
        self.file_path = Path(file_path)

    def _read_all(self) -> List[dict]:
        with open(self.file_path, encoding='utf-8') as f:
            return json.load(f)
        
    def get_all(self) -> List[PromptConfig]:
        data = self._read_all()
        return [self._map_to_entity(item) for item in data]
    
    def _map_to_entity(self, data: dict) -> PromptConfig:
        """Helper to reconstruct the objects from a dictionary."""
        system = "\n".join(data['system_content'])
        user = "\n".join(data['user_content'])
        return PromptConfig(
            system_content=system,
            user_content=user,
            name=data["name"],
            id=data["id"],
            num_predict=data["num_predict"]
        )

    def get_by_id(self, id: str) -> Optional[PromptConfig]:
        data = self._read_all()
        item = next((x for x in data if x["id"] == id), None)
        return self._map_to_entity(item) if item else None

prompts_config_repository = PromptConfigRepo()
