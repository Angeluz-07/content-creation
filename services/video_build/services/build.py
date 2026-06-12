from dataclasses import dataclass
from domain.services.build.resizer import Resizer
from domain.services.layer import LayerBuilder
from domain.services.build.assembler import Assembler
from domain.services.extractor import Extractor
from services.asset import AssetProvider
from abc import ABC, abstractmethod
from typing import List, Optional, Any


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
        layer = (
            self.layer_builder.reset()
            .set_font(font)
            .add_watermark(watermark_text)
            .add_banner_purple_bottom(hook_text)
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
        result = await self.assembler.run_async(resized, layer, output, debug=debug_frame)
        return result


class BuilderV3(BaseBuilder):

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
        result = await self.assembler.run_async(resized, layer, output, debug=debug_frame)
        return result
