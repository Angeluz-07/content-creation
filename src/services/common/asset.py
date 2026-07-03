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
        extension: Optional[str] = None
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

        self._sources[category.lower()] = {
            "path": path_obj,
            "ext": clean_ext
        }
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

    def list_source(self, category: str, recursive: bool = False) -> List[Path]:
        """
        Lists the absolute paths of all available files in a registered source.
        If the source has a registered extension, it filters the results to match it.
        
        :param category: The registered category name (e.g., 'video', 'font').
        :param recursive: If True, searches subdirectories as well.
        :return: A list of absolute Path objects.
        """
        category_key = category.lower()
        
        if category_key not in self._sources:
            raise KeyError(f"Category '{category}' has not been registered.")
            
        source_info = self._sources[category_key]
        base_path: Path = source_info["path"]
        target_ext: Optional[str] = source_info["ext"]
        
        # Verificar que el directorio realmente exista antes de escanearlo
        if not base_path.exists():
            return []
            
        # Elegimos el patrón de búsqueda según si es recursivo o no
        search_pattern = "**/*" if recursive else "*"
        
        absolute_paths = []
        
        for file_path in base_path.glob(search_pattern):
            # Nos aseguramos de listar solo archivos (ignorando subcarpetas vacías)
            if file_path.is_file():
                # Si la categoría exige una extensión específica, filtramos por ella
                if target_ext and file_path.suffix.lower() != target_ext:
                    continue
                
                # .resolve() convierte la ruta en un Absolute Path absoluto y real
                absolute_paths.append(file_path.resolve())
                
        return absolute_paths