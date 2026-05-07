from pydantic import BaseModel, Field

class ConfigInput(BaseModel):
    url: str
    force_download: bool = False
    debug_video_frame: bool = True
    start_segment: str 
    end_segment: str
    hook_text: str
    outname: str
    watermark_text: str
    frame_ts: str
    font_name: str