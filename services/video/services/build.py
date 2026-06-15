from dataclasses import dataclass
from abc import ABC, abstractmethod
from domain.services.resizer import Resizer
from domain.services.layer import LayerBuilder
from domain.services.assembler import Assembler
from domain.services.extractor import Extractor
from services.asset import AssetProvider


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
        input = params.get("input")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        resized = self.resizer.run(
            input, output_type="almost_at_top", force=force_resize
        )

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        hook_text = params.get("hook_text")
        purple_gradient = "linear-gradient(-225deg, #FF3CAC 0%, #562B7C 52%, #2B86C5 100%)"
        green_stylish = "linear-gradient(57deg, #574BCD, #2999AD, #41E975)"
        background_color = params.get("background_color", purple_gradient)
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text)
            .add_banner_bottom(hook_text, background_color)
            .run()
        )

        output = params.get("output")
        debug_frame = params.get("debug_frame")
        result = self.assembler.run(resized, layer, output, debug=debug_frame)
        return result

    async def run_async(self, params):
        input = params.get("input")
        force_resize = params.get("force_resize")
        input = self.assets.get_path("input", input)
        resized = await self.resizer.run_async(
            input, output_type="almost_at_top", force=force_resize
        )

        font_name = params.get("font_name")
        font = self.assets.get_path("font", font_name)
        watermark_text = params.get("watermark_text")
        hook_text = params.get("hook_text")
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text)
            .add_banner_purple_bottom(hook_text)
            .run()
        )

        output = params.get("output")
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
        input = params.get("input")
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

        output = params.get("output")
        debug_frame = params.get("debug_frame")
        result = self.assembler.run(resized, layer, output, debug=debug_frame)
        return result

    async def run_async(self, params):
        input = params.get("input")
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

        output = params.get("output")
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
        input = params.get("input")
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

        output = params.get("output")
        debug_frame = params.get("debug_frame")
        result = self.assembler.run(resized, layer, output, debug=debug_frame)
        return result

    async def run_async(self, params):
        input = params.get("input")
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

        output = params.get("output")
        debug_frame = params.get("debug_frame")
        result = await self.assembler.run_async(
            resized, layer, output, debug=debug_frame
        )
        return result
