from dbs.interfaces import IRepository
from domain.models import Prompt
from pathlib import Path
from typing import List, Optional, Any
import frontmatter


class MDRepository(IRepository):
    def __init__(self, directory: str):
        self.directory = Path(directory)
        print(self.directory)

    def get_all(self) -> List[Any]:
        configs = []
        for file_path in self.directory.glob("*.md"):
            configs.append(self._map_to_object(file_path))
        return configs

    def get_by_id(self, id: str) -> Optional[Any]:
        return next((x for x in self.get_all() if x.id == id), None)

    def add(self, entity: Any) -> None:
        raise NotImplementedError

    def _map_to_object(self, file_path: Path) -> Any:
        raise NotImplementedError


class PromptRepository(MDRepository):

    def __init__(self, directory: str):
        self.directory = Path(directory)

    def _map_to_object(self, file_path: Path) -> Any:
        post = frontmatter.load(file_path)

        # Separamos el contenido por los headers # System y # User
        content_parts = post.content.split("# User")
        system_content = content_parts[0].replace("# System", "").strip()
        user_content = content_parts[1].strip() if len(content_parts) > 1 else ""

        return Prompt(
            id=post["id"],
            name=post["name"],
            num_predict=post.get("num_predict", 200),
            system_content=system_content,
            user_content=user_content,
        )

    def add(self, entity: Any) -> None:
        pass
