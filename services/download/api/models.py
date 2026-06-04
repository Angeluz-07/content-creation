from pydantic import BaseModel, Field


class DownloadParamsInput(BaseModel):
    url: str
    force_download: bool = False
    start_segment: str
    end_segment: str
    output_filename: str


class DownloadVTTInput(BaseModel):
    url: str
    force_download: bool = False
    output_filename: str
