from domain.services.build.resizer import Resizer
from domain.services.build.layer_gen import LayerGenerator
from domain.services.build.assembler import Assembler

class VideoBuilderV1:
    def __init__(
        self,
        output_path: str,
        temp_path: str,
    ):
        self.output_path = output_path
        self.temp_path = temp_path

        self.resizer = Resizer(self.temp_path)
        self.layer_gen = LayerGenerator(self.temp_path)
        self.assembler = Assembler(self.temp_path, self.output_path)

    async def run(
        self,
        params,
    ):
        # fmt: off
        input_filepath    = params["input_filepath"]
        watermark_text    = params["watermark_text"]
        output_filename   = params["output_filename"]
        debug_video_frame = params["debug_video_frame"]
        hook_text         = params["hook_text"]
        font_path         = params["font_path"]
        sticker_path      = params["sticker_path"]
        force_resize      = params["force_resize"]

        resized_filepath = await self.resizer.run(input_filepath)     
        layer_filepath   = self.layer_gen.run(watermark_text, hook_text, font_path, sticker_path)
        result_path      = await self.assembler.run(resized_filepath, layer_filepath, output_filename, debug_video_frame)
        # fmt: on
        return result_path

