from src.config import (
    DOWNLOAD_DIR_AUDIO,
    ASSETS_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    VTT_DIR,
    METALS_DIR,
    IMGS_DIR,
    TEMPLATES_DIR,
)

from src.domain.common_.path import DirMap, get_path as get_path_
from functools import partial
dir_map: DirMap = {"vtt": {"base_dir": VTT_DIR, "ext": ".vtt"}}

get_path = partial(get_path_, registry=dir_map)
# assets = (
#     AssetProvider()
#     .add_source("temp", TEMP_DIR)
#     .add_source("output_videos", OUTPUT_DIR, extension=".mp4")
#     .add_source("input", DOWNLOAD_DIR_VIDEO, extension=".mp4")
#     .add_source("imgs", IMGS_DIR)
#     .add_source("templates", TEMPLATES_DIR, extension=".png")
#     .add_source("font", ASSETS_DIR, extension=".ttf")
#     .add_source("vtt", VTT_DIR, extension=".vtt")
#     .add_source("metals", METALS_DIR, extension=".json")
#     .add_source("audio", DOWNLOAD_DIR_AUDIO, extension=".m4a")
#     .add_source("transcriptions", TRANSCRIPTION_DIR, extension=".json")
# )

# storage/factory.py
import os

from src.infra.storage.azure import AzureStorageService

def get_storage_service() :
    provider = os.getenv("STORAGE_PROVIDER", "azure").lower()
    container_name = os.getenv("STORAGE_CONTAINER_NAME", "uploads")

    if provider == "azure":
        connection_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
        return AzureStorageService(connection_string=connection_str, container_name=container_name)
    
    # Próximos proveedores (ej. AWS S3)
    # elif provider == "s3":
    #     return S3StorageService(...)

    raise ValueError(f"Proveedor de storage '{provider}' no soportado")

storage_service = get_storage_service()