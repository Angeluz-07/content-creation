
from abc import ABC, abstractmethod
from typing import List, Optional, Any

class IVectorRetriever(ABC):

    @abstractmethod
    def add_vector(self, entity: Any) -> None:
        pass

    @abstractmethod
    def search_by_vector(self, entity_id: str) -> Optional[Any]:
        pass

