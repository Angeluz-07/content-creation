
from dbs.interfaces import IRepository
from pathlib import Path
from typing import List, Optional, Any
from config import PROMPTS_FOLDER, POSTS_IN_FOLDER
import frontmatter
from domain.models import Prompt, Post
import re

class MDRepository(IRepository):
    def __init__(self, directory: str):
        self.directory = Path(directory)

    def get_all(self) -> List[Any]:
        configs = []
        for file_path in self.directory.glob("*.md"):
            configs.append(self._map_to_object(file_path))
        return configs

    def get_by_id(self, id: str) -> Optional[Any]:
        # Aquí puedes optimizar buscando por nombre de archivo si prefieres
        # O simplemente filtrar el get_all()
        return next((x for x in self.get_all() if x.id == id), None)
          
    def add(self, entity: Any) -> None:
        raise NotImplementedError
    
    def _map_to_object(self, file_path: Path) -> Any:
        raise NotImplementedError

    def _parse_sections(self, content):
        # Separamos el contenido usando los encabezados "# Titulo" como delimitadores
        # El paréntesis en el regex permite que re.split mantenga los títulos en el resultado
        parts = re.split(r'^#\s+(.+)$', content, flags=re.MULTILINE)
        
        # La primera parte suele ser texto antes del primer "#" (vacío si empieza con #)
        # Saltamos el primer elemento y procesamos de 2 en 2 (Título, Contenido)
        titles = [t.strip() for t in parts[1::2]]
        bodies = [b.strip() for b in parts[2::2]]
        
        return dict(zip(titles, bodies))

class PromptRepository(MDRepository):

    def __init__(self, directory: str = str(PROMPTS_FOLDER)):
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
            examples=[]
        )

            
    def add(self, entity: Any) -> None:
        pass
    


class PostInRepository(MDRepository):

    def __init__(self, directory: str = str(POSTS_IN_FOLDER)):
        self.directory = Path(directory)


    def _map_to_object(self, file_path: Path) -> Any:
        post = frontmatter.load(file_path)
        sections = self._parse_sections(post.content)

        seed_value = list(sections.values())[0]
        content_value = list(sections.values())[1]
        content_value = content_value.replace("\n"," ")
        
        return Post(
            id=post["id"],
            seed=seed_value,
            content=content_value
        )

    def add(self, entity: Any) -> None:
        pass
