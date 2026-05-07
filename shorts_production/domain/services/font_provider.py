from pathlib import Path


class FontProvider:

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.map = self._build_map()

    def _build_map(self):
        map = {}
        for file_path in self.directory.glob("*.ttf"):
            map[file_path.stem] = str(file_path)
        return map

    def get_font(self, font_name: str):
        return self.map[font_name]
