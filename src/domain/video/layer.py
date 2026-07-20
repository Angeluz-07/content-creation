from moviepy import TextClip, CompositeVideoClip, ImageClip
from pathlib import Path
from .banner import BasicBanner


class LayerBuilder:

    def __init__(self, temp_path):
        self.temp_path = temp_path
        self._components = []

    def reset(self):
        self.font = None
        self._components = []
        return self

    def set_font(self, font_path: str):
        self._font = font_path
        return self

    def set_template(self, template_path: str):
        self._template_path = template_path
        return self

    def add_layout(self, layout_path: str):
        # 1080 * 0.666 = 720px para el ancho de lienzo optimizado
        layout = ImageClip(layout_path).resized(width=720).with_position((0, 0))
        self._components.append(layout)
        return self

    def add_emoji(
        self, emoji_path: str, coords=(7, 7)
    ):  # Coordenadas ajustadas proporcionalmente
        # 150 * 0.666 = 100px para el emoji
        emoji = ImageClip(emoji_path).resized(width=100).with_position(coords)
        self._components.append(emoji)
        return self

    def add_tag(
        self, text, font_size=37, coords=(333, 700)
    ):  # Ajustado de 55px y coords originales
        # 460*0.666 = 306, 155*0.666 = 103 para mantener proporción del recuadro
        tag = TextClip(
            text=text,
            font_size=font_size,
            color="white",
            size=(306, 103),
            font=self.font,
        ).with_position(coords)
        self._components.append(tag)
        return self

    def add_img(self, img_path: str, coords=(7, 7), zoom_factor=1):
        # Escala base cambia de 1080 a 720px
        img = (
            ImageClip(img_path)
            .resized(width=int(720 * zoom_factor))
            .with_position(coords)
        )
        self._components.append(img)
        return self

    def add_watermark(self, watermark_text, coords=(33, 60), opacity=0.5):
        # Ajustamos el tamaño de fuente (55 -> 37) y caja (460x155 -> 306x103)
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=40,
                color="white",
                size=(306, 103),
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
        # El ancho del banner ahora encaja en 720 (950 * 0.666 = 633px aprox)
        # La altura disminuye de 500 a 333px
        banner = (
            BasicBanner(
                width=633,
                height=333,
                text=text,
                font_path=self.font,
                background_color=background_color,
            )
            .render()
            .save_img(banner_filepath)
        )
        # La posición en Y se ajusta proporcionalmente al lienzo de 1280 (1150 * 0.666 = ~766)
        banner = ImageClip(banner_filepath).with_position(("center", 756))
        self._components.append(banner)
        return self

    def add_banner_black_middle(self, text):
        banner_filepath = str(Path(self.temp_path) / "banner_final.png")
        # El ancho baja de 1100 a 720 (ancho total del lienzo actual)
        # Altura baja de 320 a 213px
        banner = (
            BasicBanner(width=720, height=213, font_path=self.font, text=text)
            .render()
            .save_img(banner_filepath)
        )
        # La posición en Y se reajusta para el lienzo de 1280 (925 * 0.666 = ~616)
        banner = ImageClip(banner_filepath).with_position(("center", 616))
        self._components.append(banner)
        return self

    def run(self):
        output_png = str(Path(self.temp_path) / "temp_ui.png")
        # --- EL CAMBIO CLAVE ---
        # Ahora el lienzo de MoviePy coincide exactamente con el de tu Assembler FFmpeg.
        CANVAS_SIZE = (720, 1280)
        ui_composite = CompositeVideoClip(
            self._components, size=CANVAS_SIZE, bg_color=None
        )

        ui_composite.save_frame(output_png, t=0)
        return output_png


class LayerBuilderV2:

    def run(self, template_path, font_path, text, output_path):
        from PIL import Image, ImageDraw, ImageFont

        imagen = Image.open(template_path).convert("RGBA")
        capa_texto = Image.new("RGBA", imagen.size, (255, 255, 255, 0))
        canvas = ImageDraw.Draw(capa_texto)

        fuente = ImageFont.truetype(font_path, size=60)
        texto_dinamico = text

        # fixed for the template
        x_centro = 720 // 2
        y_pos = 920

        canvas.text(
            (x_centro, y_pos),
            texto_dinamico,
            font=fuente,
            fill="#E0E0E0",  # Blanco sólido en RGBA
            anchor="mm",  # Centro geométrico
            align="center",  # Centra las líneas de texto entre sí
            stroke_width=1,  # <--- Grosor del borde en píxeles (Prueba con 2 o 3)
            stroke_fill="#E0E0E0",  # <--- El mismo color del texto para engrosarlo
        )

        enfoque_final = Image.alpha_composite(imagen, capa_texto)

        # 8. Guardar en PNG (mantiene la transparencia del fondo si la había)
        enfoque_final.save(output_path, "PNG")
        return output_path
