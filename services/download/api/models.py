from pydantic import BaseModel, Field


class DownloadParamsInput(BaseModel):
    url: str
    force_download: bool = False
    start_segment: str
    end_segment: str
    output_filename: str


class DownloadAudioInput(BaseModel):
    url: str
    start_segment: str = "00:00:00"
    end_segment: str = "00:00:05"
    output_filename: str
    force: bool = False


class DownloadVTTInput(BaseModel):
    url: str
    force_download: bool = False
    output_filename: str
