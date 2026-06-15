from moviepy import TextClip, CompositeVideoClip, ImageClip
from pathlib import Path
from domain.services.banner import BasicBanner


class LayerBuilder:

    def __init__(self, temp_path):
        self.temp_path = temp_path
        self._font = None
        self._components = []

    def reset(self):
        self.font = None
        self._components = []
        return self

    def set_font(self, font_path: str):
        self.font = font_path
        return self

    def add_layout(self, layout_path: str):
        layout = ImageClip(layout_path).resized(width=1080).with_position((0, 0))
        self._components.append(layout)
        return self

    def add_emoji(self, emoji_path: str, coords=(10, 10)):
        emoji = ImageClip(emoji_path).resized(width=150).with_position(coords)
        self._components.append(emoji)
        return self

    def add_tag(self, text, font_size=55, coords=(500, 1050)):
        tag = TextClip(
            text=text,
            font_size=font_size,
            color="white",
            size=(460, 155),
            font=self.font,
        ).with_position(coords)
        self._components.append(tag)
        return self

    def add_img(self, img_path: str, coords=(10, 10), zoom_factor=1):
        img = (
            ImageClip(img_path)
            .resized(width=int(1080 * zoom_factor))
            .with_position(coords)
        )
        self._components.append(img)
        return self

    def add_watermark(self, watermark_text, coords=(50, 15), opacity=1):
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=55,
                color="gray",
                size=(460, 155),
                font=self.font,
            )
            .with_opacity(opacity)
            .with_position(coords)
            .rotated(15)
        )
        self._components.append(watermark)
        return self

    def add_banner_bottom(self, text, background_color):
        banner_filepath = str(Path(self.temp_path) / "banner_final.png")
        banner = (
            BasicBanner(
                width=950,
                height=500,
                text=text,
                font_path=self.font,
                background_color=background_color,
            )
            .render()  # todo: improve
            .save_img(banner_filepath)
        )
        banner = ImageClip(banner_filepath).with_position(("center", 1150))
        self._components.append(banner)
        return self

    def add_banner_black_middle(self, text):
        banner_filepath = str(Path(self.temp_path) / "banner_final.png")
        banner = (
            BasicBanner(width=1100, height=320, font_path=self.font, text=text)
            .render()
            .save_img(banner_filepath)
        )
        banner = ImageClip(banner_filepath).with_position(("center", 925))
        self._components.append(banner)
        return self

    def run(self):
        output_png = str(Path(self.temp_path) / "temp_ui.png")
        CANVAS_SIZE = (1080, 1920)
        ui_composite = CompositeVideoClip(
            self._components, size=CANVAS_SIZE, bg_color=None
        )

        ui_composite.save_frame(output_png, t=0)
        return output_png
