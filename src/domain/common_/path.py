from pathlib import Path
from typing import Dict, List, Optional, TypedDict


class DirConfig(TypedDict, total=False):
    base_dir: Path
    ext: Optional[str]


DirMap = Dict[str, DirConfig]


def get_path(
    dir_key: str,
    filename: str,
    registry: DirMap,
) -> Path:
    key = dir_key.lower()
    if key not in registry:
        raise KeyError(f"Directory key '{dir_key}' is not registered.")

    config = registry[key]
    target_path = Path(config["base_dir"]) / filename

    ext = config.get("ext")
    if ext and not target_path.suffix:
        target_path = target_path.with_suffix(ext)

    return target_path


def get_filenames(
    dir_key: str,
    registry: DirMap,
) -> List[str]:
    key = dir_key.lower()
    if key not in registry:
        raise KeyError(f"Directory key '{dir_key}' is not registered.")

    config = registry[key]
    base_dir = Path(config["base_dir"])
    ext = config.get("ext")

    if not base_dir.is_dir():
        raise FileNotFoundError(
            f"Directory for key '{dir_key}' does not exist: {base_dir}"
        )

    files = [item for item in base_dir.iterdir() if item.is_file()]
    if ext:
        files = [f for f in files if f.suffix == ext]

    return [f.name for f in files]


def get_dir_path(
    dir_key: str,
    registry: DirMap,
) -> Path:
    key = dir_key.lower()
    if key not in registry:
        raise KeyError(f"Directory key '{dir_key}' is not registered.")

    return Path(registry[key]["base_dir"])
