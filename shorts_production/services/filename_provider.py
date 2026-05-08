from pathlib import Path

#todo improve
class FilenameProvider:

    def __init__(self, directory: str, suffix:str):
        self.directory = Path(directory)
        self.suffix = suffix
        self.map = self._build_map()

    def _build_map(self):
        map = {}
        for file_path in self.directory.glob(f"*_{self.suffix}"):
            map[file_path.stem] = str(file_path)
        return map

    def get_filepath(self, font_name: str):
        return self.map[font_name]

    def get_filenames(self):
        return list(self.map.keys())