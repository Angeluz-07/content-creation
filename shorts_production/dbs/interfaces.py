from abc import ABC, abstractmethod
from typing import List, Optional, Any

class IRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Any]:
        pass

    @abstractmethod
    def add(self, entity: Any) -> None:
        pass

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[Any]:
        pass

class InMemoryDummyRepository(IRepository):
    
    def __init__(self):
        self.items = []

    def get_all(self):
        return self.items
    
    def add(self, entity: Any):
        self.items.append(entity)

    def get_by_id(self, entity_id):
        for x in self.items:
            if x.id == entity_id:
                return x
        return None