import frontmatter
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional
from config import TEXT_OUTPUT_FOLDER

@dataclass
class TextContent:
    topic: str
    text: str
    num_words: int
    creation_duration: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid4()))
    prompt_config_id: Optional[str] = None

class TextContentRepository:
    def __init__(self, directory: str = str(TEXT_OUTPUT_FOLDER)):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, content: TextContent):
        # Convertimos la dataclass a diccionario excluyendo el campo 'text'
        # porque 'text' irá en el cuerpo del markdown, no en el frontmatter.
        data = asdict(content)
        body = data.pop('text')
        
        post = frontmatter.Post(body, **data)
        
        file_path = self.directory / f"{content.id}.md"
        with open(file_path, "wb") as f:
            frontmatter.dump(post, f)

    def get_by_id(self, id: str) -> Optional[TextContent]:
        file_path = self.directory / f"{id}.md"
        if not file_path.exists():
            return None
        
        post = frontmatter.load(file_path)
        return self.map_to_entity(post.metadata, post.content)

    def map_to_entity(self, metadata: dict, content_body: str) -> TextContent:
        """
        Mapea los datos del archivo markdown a la entidad TextContent.
        """
        # Aseguramos que la fecha sea un objeto datetime si viene de una carga simple
        created_at = metadata.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return TextContent(
            topic=metadata.get('topic'),
            text=content_body,
            num_words=metadata.get('num_words'),
            creation_duration=metadata.get('creation_duration'),
            created_at=created_at,
            id=metadata.get('id'),
            prompt_config_id=metadata.get('prompt_config_id')
        )
