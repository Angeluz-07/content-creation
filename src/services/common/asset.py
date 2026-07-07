from pathlib import Path
from typing import Dict, Union, Optional, List


class AssetProvider:

    def __init__(self):
        # Maps category -> {"path": Path, "ext": optional_string_extension}
        self._sources: Dict[str, dict] = {}

    def add_source(
        self,
        category: str,
        directory_path: Union[str, Path],
        extension: Optional[str] = None,
    ) -> "AssetProvider":
        """
        Registers a base directory for a category, with an optional forced extension.

        Examples:
            provider.add_source("font", "./assets/shared_folder", extension=".ttf")
            provider.add_source("img", "./assets/shared_folder", extension="png")
        """
        path_obj = Path(directory_path)

        # Clean up extension format (ensure it starts with a dot if provided)
        clean_ext = None
        if extension:
            clean_ext = extension if extension.startswith(".") else f".{extension}"
            clean_ext = clean_ext.lower()

        self._sources[category.lower()] = {"path": path_obj, "ext": clean_ext}
        return self

    def get_path(self, category: str, filename: str) -> Path:
        """
        Returns the full Path object. Automatically appends the registered
        extension if it wasn't already provided in the filename.
        """
        category_key = category.lower()

        if category_key not in self._sources:
            raise KeyError(f"Category '{category}' has not been registered.")

        source_info = self._sources[category_key]
        base_path = source_info["path"]
        target_ext = source_info["ext"]

        target_path = base_path / filename

        # If an extension was registered and the requested filename doesn't
        # already end with it, append it automatically.
        if target_ext and target_path.suffix.lower() != target_ext:
            target_path = target_path.with_suffix(target_ext)

        return str(target_path)

    def get_filenames(self, category: str) -> list[Path]:
        """
        Lists all available files in the directory of the given category.
        If the category has a registered extension, it filters by it.
        """
        category_key = category.lower()
        
        if category_key not in self._sources:
            raise KeyError(f"Category '{category}' has not been registered.")
            
        source_info = self._sources[category_key]
        base_path = source_info["path"]
        target_ext = source_info["ext"]
        
        # Validar que el directorio exista antes de listar
        if not base_path.is_dir():
            raise FileNotFoundError(f"The directory for category '{category}' does not exist: {base_path}")
            
        # Listar solo archivos
        files = (item for item in base_path.iterdir() if item.is_file())
        files = (Path(item).name for item in files)
        files = list(files)
        files.reverse()
        return files
