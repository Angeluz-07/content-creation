from abc import ABC, abstractmethod
from typing import List, Optional, Any


class IVectorStore(ABC):

    @abstractmethod
    def add(self) -> None:
        pass

    @abstractmethod
    def search(self):
        pass
