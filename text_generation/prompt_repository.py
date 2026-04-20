from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from config import PROMPTS_FOLDER
import frontmatter

@dataclass
class Prompt:
    system_content: str
    user_content: str
    id: str 
    name: str
    num_predict: int = 200

class PromptRepository:
    def __init__(self, directory: str = str(PROMPTS_FOLDER)):
        self.directory = Path(directory)

    def get_all(self) -> List[Prompt]:
        configs = []
        for file_path in self.directory.glob("*.md"):
            configs.append(self._map_to_entity(file_path))
        return configs

    def _map_to_entity(self, file_path: Path) -> Prompt:
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
            user_content=user_content
        )

    def get_by_id(self, id: str) -> Optional[Prompt]:
        # Aquí puedes optimizar buscando por nombre de archivo si prefieres
        # O simplemente filtrar el get_all()
        return next((x for x in self.get_all() if x.id == id), None)
    

