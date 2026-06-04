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
