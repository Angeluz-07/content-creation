from pydantic import BaseModel, Field


class DownloadInput(BaseModel):
    url: str
    force_download: bool = False
    start_segment: str
    end_segment: str
    output_filename: str
    file_type: str = "vtt"


class DiscoveryInput(BaseModel):
    input_filename: str
    output_filename: str
    sensitivity: float = 0.75
    min_words: int = 80
    url: str


class ProductionInput(BaseModel):
    input_filename: str
    font_name: str
    watermark_text: str
    frame_ts: str
    hook_text: str
    output_filename: str
    debug_frame: bool = True
    background_color: str


class TaskSyncInput(BaseModel):
    task_id: str
    status: str
