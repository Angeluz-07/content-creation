from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from src.services.common.asset import AssetProvider
from src.domain.video.resizer import resize_zoomed_square_async
from src.domain.video.layer import add_text_to_template
from src.domain.video.assembler import assemble_video_and_template_async


@dataclass
class BaseBuilder(ABC):
    assets: AssetProvider

    @abstractmethod
    def run(self):
        pass


class BuilderV4(BaseBuilder):

    def run(self, params):
        input = params.get("input_filename")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        resized = self.resizer.run(
            input, output_type="almost_at_top", force=force_resize
        )

        template_name = "template_fp.png"
        template_name = "template_bM.png"
        template_path = self.assets.get_path("temp", template_name)
        font_name = "GoogleSans-Bold"
        font_path = self.assets.get_path("font", font_name)
        hook_text = params.get("hook_text")
        layer = self.assets.get_path("temp", "temp_ui.png")  #
        layer = self.layer_builder.run(
            template_path,
            font_path,
            hook_text,
            output_path=layer,
        )

        output = params.get("output_filename")
        debug_frame = params.get("debug_frame")
        result = self.assembler.run(resized, layer, output, debug=debug_frame)
        return result

    async def run_async(self, params):
        input_filename = params.get("input_filename")
        force_resize = params.get("force_resize", True)
        input = self.assets.get_path("input", input_filename)
        resized = self.assets.get_path("temp", "temp_resized.mp4")  #
        resized = await resize_zoomed_square_async(input, resized, force=force_resize)

        template_name = "template_fp.png"
        # template_name = "template_bM.png"
        template_path = self.assets.get_path("temp", template_name)
        font_name = "GoogleSans-Bold"
        font_path = self.assets.get_path("font", font_name)
        hook_text = params.get("hook_text")
        hook_text = hook_text.replace("\\n", "\n")
        layer = self.assets.get_path("temp", "temp_ui.png")  #
        layer = add_text_to_template(
            template_path,
            font_path,
            hook_text,
            output_path=layer,
        )

        output = params.get("output_filename")
        output_path = self.assets.get_path("output_videos", output)
        debug_frame = params.get("debug_frame")
        result = assemble_video_and_template_async(
            resized, output_path, layer, debug=debug_frame
        )
        return result
