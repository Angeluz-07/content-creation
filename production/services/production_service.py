from uuid import uuid4
from typing import Dict
import requests


class ProductionService:
    def __init__(
        self,
        video_builder,
        filepath_provider,
        fontpath_provider,
        validator=None,
    ):
        self.video_builder = video_builder
        self.filepath_provider = filepath_provider
        self.fontpath_provider = fontpath_provider
        self.validator = validator
        self.url = "http://localhost:8003"

    def trigger_sync(self, params: Dict):
        input_filename = params["input_filename"]
        font_name = params["font_name"]
        watermark_text = params["watermark_text"]
        frame_ts = params["frame_ts"]
        hook_text = params["hook_text"]
        output_filename = params["output_filename"]
        debug_video_frame = params["debug_video_frame"]

        response = requests.post(
            f"{self.url}/produce-short/synchronous",
            json={
                "input_filename": input_filename,
                "font_name": font_name,
                "watermark_text": watermark_text,
                "frame_ts": frame_ts,
                "hook_text": hook_text,
                "output_filename": output_filename,
                "debug_video_frame": debug_video_frame,
            },
        )

    def trigger_async(self, params: Dict):
        input_filename = params["input_filename"]
        font_name = params["font_name"]
        watermark_text = params["watermark_text"]
        frame_ts = params["frame_ts"]
        hook_text = params["hook_text"]
        output_filename = params["output_filename"]
        debug_video_frame = params["debug_video_frame"]

        response = requests.post(
            f"{self.url}/produce-short",
            json={
                "input_filename": input_filename,
                "font_name": font_name,
                "watermark_text": watermark_text,
                "frame_ts": frame_ts,
                "hook_text": hook_text,
                "output_filename": output_filename,
                "debug_video_frame": debug_video_frame,
            },
        )

    def validate(self, params):
        self.validator.validate(params)

    def run(self, params):
        print("Processing ", params["input_filename"])
        # fmt: off
        _params = {}
        _params["input_filepath"]    = self.filepath_provider.get_filepath(params["input_filename"])
        _params["watermark_text"]    = params["watermark_text"]
        _params["output_filename"]   = params["output_filename"]
        _params["debug_video_frame"] = params["debug_video_frame"]
        _params["hook_text"]         = params["hook_text"]
        _params["frame_ts"]          = params["frame_ts"]
        _params["font_path"]         = self.fontpath_provider.get_font(params["font_name"]) 
        _params["force_resize"]      = False
        
        result_path    = self.video_builder.build(_params) 

        print("Video produced at ", result_path)
        # fmt: on

    def get_new_uuid(self):
        return str(uuid4())
