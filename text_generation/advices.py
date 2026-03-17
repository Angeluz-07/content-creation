from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
from dataclasses import asdict
from datetime import timezone

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FOLDER = BASE_DIR / ".data"
ADVICES_FILE_PATH = DATA_FOLDER / "advices.json"

@dataclass
class Advice:
    topic: str
    text: str
    num_words: int
    creation_duration: float
    created_at: datetime = field(default_factory= lambda : datetime.now(timezone.utc))
    id:  str = field(default_factory=lambda: str(uuid4()))
    prompt_config_id: str = None
    
    def __str__(self):
        return f'Advice(topic={self.topic}, id={self.id})'

class AdviceRepo:
    def __init__(self, file_path: str = ADVICES_FILE_PATH):
        self.file_path = Path(file_path)
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        if not self.file_path.exists():
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)

    def _read_all(self) -> List[dict]:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_all(self, data: List[dict]):
        with open(self.file_path, 'w',encoding='utf-8') as f:
            json.dump(data, f,ensure_ascii=False, indent=4)
    

    def get_all(self) -> List[Advice]:
        data = self._read_all()
        return [self._map_to_entity(item) for item in data]
    
    def _map_to_entity(self, data: dict) -> Advice:
        """Helper to reconstruct the objects from a dictionary."""
        return Advice(
            topic=data['topic'],
            text=data['text'],
            num_words=data['num_words'],
            created_at=datetime.fromisoformat(data['created_at']),
            creation_duration=data["creation_duration"],
            id=data['id'],
            prompt_config_id=data["prompt_config_id"]
        )

    def get_by_id(self, id: str) -> Optional[Advice]:
        data = self._read_all()
        item = next((x for x in data if x["id"] == id), None)
        return self._map_to_entity(item) if item else None

    def add(self, item: Advice):
        data = self._read_all()
        # Convert dataclass to dict; datetime handled by custom logic
        item_dict = asdict(item)
      
        # Convert datetime objects to ISO strings for JSON
        if isinstance(item_dict['created_at'], datetime):
            item_dict['created_at'] = item_dict['created_at'].isoformat()
        
        data.append(item_dict)
        self._write_all(data)

advice_repository = AdviceRepo()

#from pprint import pprint
#pprint(advice_repository.get_all())