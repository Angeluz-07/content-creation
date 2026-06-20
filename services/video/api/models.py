from pydantic import BaseModel, Field


class ProductionInput(BaseModel):
    task_id: str
    input_filename: str
    font_name: str
    watermark_text: str
    frame_ts: str
    hook_text: str
    output_filename: str
    debug_frame: bool = True