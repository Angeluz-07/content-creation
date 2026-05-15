import skia
import re


class SkiaCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = skia.Surface(self.width, self.height)
        self.canvas = self.surface.getCanvas()
        # Almacenamos la geometría actual aquí
        self._current_path = None

    def _hex_to_color(self, hex_str):
        h = hex_str.lstrip("#")
        if len(h) == 3:
            h = "".join([c * 2 for c in h])
        return skia.ColorSetARGB(255, int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    # --- Métodos de Geometría (Construyen la forma) ---

    def add_rectangle(self):
        """Define un rectángulo que ocupa todo el canvas"""
        self._current_path = skia.Path()
        self._current_path.addRect(skia.Rect(0, 0, self.width, self.height))
        return self

    # --- Métodos de Estilo (Pintan la forma guardada) ---

    def add_background_color(self, color_or_gradient):
        """Aplica color o degradado a la forma construida previamente"""
        if self._current_path is None:
            raise ValueError(
                "Debes construir una forma (build_*) antes de aplicar color."
            )

        paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kFill_Style)

        if "linear-gradient" in color_or_gradient:
            colors_hex = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}", color_or_gradient)
            stops = [float(s) / 100 for s in re.findall(r"(\d+)%", color_or_gradient)]
            sk_colors = [self._hex_to_color(h) for h in colors_hex]

            # El gradiente se adapta a los límites de la forma actual
            bounds = self._current_path.getBounds()
            pts = [
                skia.Point(bounds.fLeft, bounds.fTop),
                skia.Point(bounds.fRight, bounds.fBottom),
            ]

            paint.setShader(skia.GradientShader.MakeLinear(pts, sk_colors, stops))
        else:
            paint.setColor(self._hex_to_color(color_or_gradient))

        # Dibujamos el path actual con el estilo definido
        self.canvas.drawPath(self._current_path, paint)
        return self

    def get_img(self):
        return self.surface.makeImageSnapshot()

    def save_img(self, path):
        self.get_img().save(str(path), skia.kPNG)
        return self


class BasicBanner(SkiaCanvas):
    """
    Basic rectangle banner with white text and black background
    """

    def __init__(self, width, height, text, font_path):
        self.params = {
            "width": width,
            "height": height,
            "padding": 60,
            "font_size": 90,
            "line_spacing": 1.1,
            "letter_spacing": 0.05,
            "text_color": "#E0E0E0",
            "background_color": "#000000",
            # "background_color": "linear-gradient(-225deg, #FF3CAC 0%, #562B7C 52%, #2B86C5 100%) "
        }
        super().__init__(self.params["width"], self.params["height"])

        self.text = text
        self.font_path = font_path

    def set_background_color(self, color_or_gradient):
        self.params["background_color"] = color_or_gradient
        return self

    def set_text_color(self, color):
        self.params["text_color"] = color
        return self

    def add_font(self, font_path):
        typeface = skia.Typeface.MakeFromFile(font_path)
        self.font = skia.Font(typeface, self.params["font_size"])
        self.font.setSubpixel(True)
        self.font.setEdging(skia.Font.Edging.kAntiAlias)
        self.font.setEmbolden(True)
        return self

    def add_text(self, text: str):
        if self.font is None:
            raise ValueError("Must call with_font first")

        # Usamos el TextEngine externo
        lines = self._get_wrapped_lines(text)

        paint = skia.Paint(
            AntiAlias=True, Color=self._hex_to_color(self.params["text_color"])
        )

        line_h = self.font.getSize() * self.params["line_spacing"]
        total_h = len(lines) * line_h
        y_ptr = (self.height / 2) - (total_h / 2) + (self.font.getSize() * 0.75)

        for line in lines:
            line_w = self.font.measureText(line) + (
                len(line) * self.font.getSize() * self.params["letter_spacing"]
            )
            x = (self.width - line_w) / 2
            self.canvas.drawSimpleText(line, x, y_ptr, self.font, paint)
            y_ptr += line_h

        return self

    def render(self):
        return (
            self.add_rectangle()
            .add_background_color(self.params["background_color"])
            .add_font(self.font_path)
            .add_text(self.text)
        )

    def _get_wrapped_lines(self, text_content: str):
        """
        given a text, splitted into lines, so it can fit container
        """
        max_w = self.width - (self.params["padding"] * 2)
        paragraphs = text_content.split("\n")
        final_lines = []

        for paragraph in paragraphs:
            words = paragraph.split(" ")
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                # Cálculo de ancho con tracking
                w = self.font.measureText(test_line) + (
                    len(test_line) * self.font.getSize() * self.params["letter_spacing"]
                )
                if w > max_w and current_line:
                    final_lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            final_lines.append(current_line)
        return final_lines
