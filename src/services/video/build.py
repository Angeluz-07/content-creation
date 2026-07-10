from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.domain.video.resizer import Resizer
from src.domain.video.layer import LayerBuilder
from src.domain.video.assembler import Assembler
from src.domain.video.extractor import Extractor
from src.services.common.asset import AssetProvider

# todo: move to domain layer
COLOR_MAP = {
    "purple-gradient": "linear-gradient(-225deg, #FF3CAC 0%, #562B7C 52%, #2B86C5 100%)",
    "green-stylish": "linear-gradient(57deg, #574BCD, #2999AD, #41E975)",
    "black-serious": "linear-gradient(180deg, #1F2124, #111215)",
    "purple-sober": "linear-gradient(to right, #24243e, #302b63, #0f0c29)",
    "purple-fun": "linear-gradient(315deg, #4F00BC 0%, #29007B 100%)",
    "green-leaf": "linear-gradient(-225deg, #7A9D54 0%, #557A46 55%, #1A3C1E 100%)"
}


@dataclass
class BaseBuilder(ABC):
    assets: AssetProvider
    resizer: Resizer
    layer_builder: LayerBuilder
    assembler: Assembler
    extractor: Extractor

    @abstractmethod
    def run(self):
        pass


class BuilderV1(BaseBuilder):
    """
    First version of video builder, with zoomed video,
    watermark text, simple comment emoji and text.
    Original the font used was cascadiacode.ttf.
    """

    def run(self, params):
        input = params.get("input_filename")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        resized = self.resizer.run(
            input, output_type="almost_at_top", force=force_resize
        )

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        hook_text = params.get("hook_text")
        background_color = params.get("background_color", "black-serious")
        background_color = COLOR_MAP.get(background_color)
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text)
            .add_banner_bottom(hook_text, background_color)
            .run()
        )

        output = params.get("output_filename")
        debug_frame = params.get("debug_frame")
        result = self.assembler.run(resized, layer, output, debug=debug_frame)
        return result

    async def run_async(self, params):
        input = params.get("input_filename")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        resized = await self.resizer.run_async(
            input, output_type="almost_at_top", force=force_resize
        )

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        hook_text = params.get("hook_text")
        hook_text = hook_text.replace("\\n", "\n")
        background_color = params.get("background_color", "black-serious")
        background_color = COLOR_MAP.get(background_color)
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text)
            .add_banner_bottom(hook_text, background_color)
            .run()
        )

        output = params.get("output_filename")
        debug_frame = params.get("debug_frame")
        result = await self.assembler.run_async(
            resized, layer, output, debug=debug_frame
        )
        return result


class BuilderV2(BaseBuilder):
    """
    Second version of video builder, with zoomed video at the top,
    hook text inthe middle, with custom font. And frame at the bottom
    section. Main font is ProtestStrike-Regular.ttf
    """

    def run(self, params):
        input = params.get("input_filename")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        resized = self.resizer.run(input, output_type="at_top", force=force_resize)

        frame = self.extractor.run(input, timestamp="00:00:02")

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        hook_text = params.get("hook_text")
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text, coords=(0, 5))
            .add_img(frame, coords=("center", 1200), zoom_factor=1.3)
            .add_banner_black_middle(hook_text)
            .run()
        )

        output = params.get("output_filename")
        debug_frame = params.get("debug_frame")
        result = self.assembler.run(resized, layer, output, debug=debug_frame)
        return result

    async def run_async(self, params):
        input = params.get("input_filename")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        resized = await self.resizer.run_async(
            input, output_type="at_top", force=force_resize
        )

        frame = await self.extractor.run_async(input, timestamp="00:00:02")

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        hook_text = params.get("hook_text")
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text, coords=(0, 5))
            .add_img(frame, coords=("center", 1200), zoom_factor=1.3)
            .add_banner_black_middle(hook_text)
            .run()
        )

        output = params.get("output_filename")
        debug_frame = params.get("debug_frame")
        result = await self.assembler.run_async(
            resized, layer, output, debug=debug_frame
        )
        return result


class BuilderV3(BaseBuilder):
    """
    Third version of video builder:
        - receives video with zoom, rescaled to mobile canvas
        - given a value 'percentage' we can slide the portion
        to keep.
        - adds watermark
    """

    def run(self, params):
        input = params.get("input_filename")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        percentage = params.get("percentage")
        resized = self.resizer.run(
            input,
            output_type="full_vertical",
            force=force_resize,
            percentage=percentage,
        )

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text, coords=(0, 5))
            .run()
        )

        output = params.get("output_filename")
        debug_frame = params.get("debug_frame")
        result = self.assembler.run(resized, layer, output, debug=debug_frame)
        return result

    async def run_async(self, params):
        input = params.get("input_filename")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        percentage = params.get("percentage")
        resized = await self.resizer.run_async(
            input,
            output_type="full_vertical",
            force=force_resize,
            percentage=percentage,
        )

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text, coords=(0, 5))
            .run()
        )

        output = params.get("output_filename")
        debug_frame = params.get("debug_frame")
        result = await self.assembler.run_async(
            resized, layer, output, debug=debug_frame
        )
        return result
