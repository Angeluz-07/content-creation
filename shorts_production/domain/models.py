from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Config:
    url: str
    start_segment: str
    end_segment: str
    hook_text: str
    outname: str
    watermark_text: str
    frame_ts: str
    font_name: str
    force_download: bool = False
    debug_video_frame: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class ShortProductionParams:
    filename: str
    font_name: str
    watermark_text: str
    frame_ts: str
    hook_text: str
    debug_video_frame: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class DownloadParams:
    url: str  
    start_segment: str
    end_segment: str
    filename: str
    force_download: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))