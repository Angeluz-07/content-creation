from dataclasses import dataclass, field


@dataclass
class Config:
    url: str
    start_segment: str
    end_segment: str
    hook_text: str
    outname: str
    watermark_text: str
    force_download: bool = False
    debug_video_frame: bool = True
