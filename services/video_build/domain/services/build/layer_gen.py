from moviepy import TextClip, CompositeVideoClip, ImageClip
from pathlib import Path


class LayerGenerator:

    def __init__(self, temp_path):
        self.temp_path = temp_path

    def run(self, watermark_text, hook_text, font_path, sticker_path):
        hook_text_cleaned = hook_text.replace(r"\n", "\n")
        layer_path = self._generate_fixed_layer(
            watermark_text, hook_text_cleaned, font_path, sticker_path
        )
        return layer_path

    # v1, todo: migrate v2 and v3
    def _generate_fixed_layer(self, watermark_text, hook_text, font_path, sticker_path):
        output_png = str(Path(self.temp_path) / "temp_ui.png")
        CANVAS_SIZE = (1080, 1920)

        hook = TextClip(
            text=hook_text,
            font_size=100,
            color="white",
            bg_color="black",
            method="caption",
            size=(920, 350),
            text_align="center",
            vertical_align="center",
            font=font_path,
        ).with_position(("center", 1150))

        # Watermark
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=55,
                color="gray",
                size=(460, 155),
                font=font_path,
            )
            .with_position((50, 15))
            .rotated(15)
        )

        # Logo
        # logo_path = str(Path(self.assets_path) / "emoji_comment.png")
        logo = ImageClip(sticker_path).resized(width=150).with_position((860, 1035))

        # Componemos y guardamos UN SOLO FRAME
        ui_composite = CompositeVideoClip(
            [hook, watermark, logo], size=CANVAS_SIZE, bg_color=None
        )

        ui_composite.save_frame(output_png, t=0)
        return output_png
