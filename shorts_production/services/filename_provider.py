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

    def get_filepath(self, filename: str):
        return self.map[filename]

    def get_filenames(self):
        result = list(self.map.keys())
        result.reverse()
        return result