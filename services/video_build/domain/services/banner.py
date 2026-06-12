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

    def add_rectangle(self, corner_radius=0):
        """Define un rectángulo que ocupa todo el canvas"""
        self._current_path = skia.Path()
        rect = skia.Rect(0, 0, self.width, self.height)
        self._current_path.addRoundRect(rect, corner_radius, corner_radius)
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

    def render_purple(self):
        return (
            self.add_rectangle(corner_radius=90)
            .add_background_color(
                "linear-gradient(-225deg, #FF3CAC 0%, #562B7C 52%, #2B86C5 100%)"
            )
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


class StackedBanner(SkiaCanvas):
    """
    Banner de capas apiladas con efecto de profundidad (Estilo Farándula)
    """

    def __init__(self, width, height, main_text, sub_text, font_path):
        c_opts = [
            ("#FFC107", "#9C27B0"),
            ("#FFD700", "#6A0DAD"),
            ("#FFF2B2", "#4A0E4E"),
            ("#FDF5C9", "#3D1075"),
            ("#FFEAA7", "#530A3B"),
        ]
        c = c_opts[4]
        self.params = {
            "width": width,
            "height": height,
            "padding": 80,
            "font_size_main": 85,
            "font_size_sub": 70,
            "color_back": c[0],  # Capa de fondo (desfasada)
            "color_front": c[1],  # Capa principal
            "color_tag": "#FFFFFF",  # Capa del sujeto
            "text_color_main": "#FFFFFF",
            "text_color_sub": "#000000",
            "line_spacing": 1.1,
            "letter_spacing": 0.05,
        }
        super().__init__(self.params["width"], self.params["height"])

        self.main_text = main_text
        self.sub_text = sub_text
        self.font_path = font_path
        self.sk_font_main = None
        self.sk_font_sub = None

        # Filtro de sombra preconfigurado
        self.shadow = skia.ImageFilters.DropShadow(
            dx=8, dy=8, sigmaX=12, sigmaY=12, color=skia.ColorSetARGB(150, 0, 0, 0)
        )

    def add_fonts(self, font_path):
        typeface = skia.Typeface.MakeFromFile(font_path)
        # Fuente Principal
        self.sk_font_main = skia.Font(typeface, self.params["font_size_main"])
        self.sk_font_main.setSubpixel(True)
        self.sk_font_main.setEdging(skia.Font.Edging.kAntiAlias)
        self.sk_font_main.setEmbolden(True)

        # Fuente Secundaria (Tag)
        self.sk_font_sub = skia.Font(typeface, self.params["font_size_sub"])
        self.sk_font_sub.setSubpixel(True)
        self.sk_font_sub.setEdging(skia.Font.Edging.kAntiAlias)
        return self

    def _draw_stacked_containers(self):
        # 1. Capa de Fondo
        paint_back = skia.Paint(
            AntiAlias=True,
            Color=self._hex_to_color(self.params["color_back"]),
            ImageFilter=self.shadow,
        )
        rect_back = skia.Rect.MakeXYWH(100, 100, self.width - 200, self.height - 220)
        self.canvas.drawRoundRect(rect_back, 40, 40, paint_back)

        # 2. Capa Frontal
        paint_front = skia.Paint(
            AntiAlias=True, Color=self._hex_to_color(self.params["color_front"])
        )
        rect_front = skia.Rect.MakeXYWH(80, 80, self.width - 200, self.height - 240)
        self.canvas.drawRoundRect(rect_front, 30, 30, paint_front)

        return rect_front  # Retornamos para saber dónde escribir el texto

    def _draw_main_text(self, container_rect):
        lines = self._get_wrapped_lines(
            self.main_text, self.sk_font_main, container_rect.width() - 80
        )
        paint = skia.Paint(
            AntiAlias=True, Color=self._hex_to_color(self.params["text_color_main"])
        )

        line_h = self.sk_font_main.getSize() * self.params["line_spacing"]
        # Posición inicial centrada en el contenedor frontal
        y_ptr = (
            container_rect.fTop
            + (container_rect.height() / 2)
            - ((len(lines) - 1) * line_h / 2)
            + 20
        )

        for line in lines:
            line_w = self.sk_font_main.measureText(line)
            x = container_rect.fLeft + (container_rect.width() - line_w) / 2
            self.canvas.drawSimpleText(line, x, y_ptr, self.sk_font_main, paint)
            y_ptr += line_h

    def _draw_tag(self):
        # Calcular ancho del tag según el texto
        text_w = self.sk_font_sub.measureText(self.sub_text)
        tag_w = text_w + 100
        tag_h = 100

        paint_tag = skia.Paint(
            AntiAlias=True,
            Color=self._hex_to_color(self.params["color_tag"]),
            ImageFilter=self.shadow,
        )

        x_tag = (self.width - tag_w) / 2
        y_tag = 310  # Posición que "pisa" el borde inferior

        rect_tag = skia.Rect.MakeXYWH(x_tag, y_tag, tag_w, tag_h)
        self.canvas.drawRoundRect(rect_tag, 20, 20, paint_tag)

        # Texto del Tag
        paint_txt = skia.Paint(
            AntiAlias=True, Color=self._hex_to_color(self.params["text_color_sub"])
        )
        self.canvas.drawSimpleText(
            self.sub_text,
            x_tag + (tag_w - text_w) / 2,
            y_tag + 70,
            self.sk_font_sub,
            paint_txt,
        )

    def render(self):
        self.add_fonts(self.font_path)
        front_rect = self._draw_stacked_containers()
        self._draw_main_text(front_rect)
        # self._draw_tag()
        return self

    def _get_wrapped_lines(self, text, font, max_w):
        # Lógica de wrap idéntica a la anterior pero recibe parámetros dinámicos
        paragraphs = text.split("\n")
        final_lines = []
        for p in paragraphs:
            words = p.split(" ")
            curr = ""
            for w in words:
                test = f"{curr} {w}".strip()
                if font.measureText(test) > max_w:
                    final_lines.append(curr)
                    curr = w
                else:
                    curr = test
            final_lines.append(curr)
        return final_lines
