from pathlib import Path

class PromptRepository:
    def __init__(self, folder_path: str | Path):
        self.folder = Path(folder_path)

    def _resolve_path(self, name: str) -> Path:
        path = self.folder / f"{name}.md"
        if path.is_file():
            return path

        for p in self.folder.glob("**/*.md"):
            if p.stem == name:
                return p

        raise FileNotFoundError(f"Prompt '{name}' no encontrado en {self.folder}")

    def get(self, name: str) -> tuple[dict, str]:
        path = self._resolve_path(name)
        content = path.read_text(encoding="utf-8").strip()

        metadata = {}
        body = content

        # Extraer metadatos sencillos
        if content.startswith("---"):
            _, meta_block, body = content.split("---", 2)
            for line in meta_block.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip()] = v.strip()

        # Limpiar prefijo # system si existe al inicio
        body = body.strip()
        for prefix in ("# system", "#system"):
            if body.lower().startswith(prefix):
                body = body[len(prefix):]
                break

        return metadata, body.strip()