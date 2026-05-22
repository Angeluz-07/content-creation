from pydantic import BaseModel, Field


class ShortProductionParamsInput(BaseModel):
    input_filename: str
    font_name: str
    watermark_text: str
    frame_ts: str
    hook_text: str
    output_filename: str
    debug_video_frame: bool = True


class DownloadParamsInput(BaseModel):
    url: str
    force_download: bool = False
    start_segment: str
    end_segment: str
    output_filename: str
