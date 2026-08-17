from functools import partial
from src.domain.download.services import download_vtt as download_vtt_
from src.domain.download.services import download_video as download_video_
from src.domain.download.services import download_audio as download_audio_
from src.config import DOWNLOAD_DIR, COOKIES_PATH, VTT_DIR, VIDEO_DIR_DOWNLOAD, DOWNLOAD_DIR_AUDIO


download_vtt = partial(download_vtt_, output_dir=VTT_DIR, cookies_path=COOKIES_PATH)
download_video = partial(download_video_, output_dir=VIDEO_DIR_DOWNLOAD, cookies_path=COOKIES_PATH)
download_audio = partial(download_audio_, output_dir=DOWNLOAD_DIR_AUDIO, cookies_path=COOKIES_PATH)

