from pydantic import BaseModel, Field


class ProductionInput(BaseModel):
    input: str
    font_name: str
    watermark_text: str
    frame_ts: str
    hook_text: str
    output: str
    debug_frame: bool = True