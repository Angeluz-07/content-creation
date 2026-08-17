from src.services.video.build import build_v1 as build_v1_
from src.config import (
    VIDEO_DIR_DOWNLOAD,
    VIDEO_DIR_OUTPUT,
    TEMP_DIR,
    TEMPLATES_DIR,
    FONTS_DIR,
)


async def build_v1(params: dict):
    return await build_v1_(
        params, VIDEO_DIR_DOWNLOAD, VIDEO_DIR_OUTPUT, TEMP_DIR, TEMPLATES_DIR, FONTS_DIR
    )
