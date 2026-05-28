from uuid import uuid4


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
