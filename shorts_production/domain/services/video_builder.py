import subprocess
from pathlib import Path
from moviepy import TextClip, CompositeVideoClip, ImageClip
from moviepy.video.tools.drawing import color_gradient
from domain.services.banner import BasicBanner
from html2image import Html2Image
from PIL import ImageFont

from pathlib import Path
import re
import skia

class VideoBuilderV2:
    """
    Second version of video builder, with zoomed video at the top,
    hook text inthe middle, with custom font. And frame at the bottom
    section. Main font is ProtestStrike-Regular.ttf
    """
    def __init__(
        self,
        output_path: str,
        temp_path: str,
        font_path: str,
        assets_path: str,
    ):
        self.output_path = output_path
        self.temp_path = temp_path
        self.font_path = font_path
        self.assets_path = assets_path

    def build(
        self,
        input_filepath: str,
        file_id: str,
        watermark_text: str,
        hook_text: str,
        debug_video_frame: str,
        frame_ts: str
    ):
        hook_text_cleaned = hook_text.replace(r"\n", "\n")

        # fmt: off
        resized_filepath     = self._resize_video_segment(input_filepath, file_id)
        frame_filepath       = self._get_video_frame(input_filepath, frame_ts)
        fixed_layer_filepath = self._generate_fixed_layer(watermark_text, hook_text_cleaned, frame_filepath)
        result_path          = self._assemble(resized_filepath, fixed_layer_filepath, file_id, debug_video_frame)
        # fmt: on
        return result_path

    def _resize_video_segment(self, input_filepath: str, file_id: str):
        resized_filepath = str(Path(self.temp_path) / f"{file_id}_resized.mp4")
        resized_file_exists = Path(resized_filepath).is_file()

        if not resized_file_exists:
            print("Resized file doesnt exists. Start resizing...")
            try:
                POS_Y = 0
                CANVAS_W, CANVAS_H = 1080, 1920
                ZOOM_FACTOR = 1.53
                TARGET_W = int(CANVAS_W * ZOOM_FACTOR)  # 1620px

                safe_filter = (
                    # 1. Escalamos el VIDEO para que el ancho sea 1620.
                    # La altura se ajusta sola (-1) para no achatar.
                    f"scale={TARGET_W}:-1,"
                    # 2. Forzamos que los píxeles sean cuadrados.
                    "setsar=1:1,"
                    # 3. CORTAMOS el video al ancho del lienzo (1080).
                    # Esto elimina los bordes laterales que sobran por el zoom (el overflow).
                    # 'ih' mantiene la altura que resultó del escalado anterior.
                    f"crop={CANVAS_W}:ih,"
                    # 4. Ponemos el video en el lienzo vertical.
                    # Ahora 'iw' es exactamente 1080, así que no habrá error.
                    f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black"
                )
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-stats",
                    "-i",
                    input_filepath,
                    "-vf",
                    safe_filter,
                    "-c:v",
                    "h264_amf",
                    "-rc",
                    "cbr",
                    "-b:v",
                    "18M",  # Subimos a 18M para que el zoom no pierda nitidez
                    "-quality",
                    "quality",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    resized_filepath,
                ]
                print("Resizing video for mobile canvas...")
                subprocess.run(ffmpeg_cmd, check=True)

                print(f"Resizing successful with file: {resized_filepath}")
                return resized_filepath
            except subprocess.CalledProcessError as e:
                print(f"Error while resizing : {e}")
                raise
        else:
            print("Resized file exists. Skipping resizing...")
            return resized_filepath

    def _get_video_frame(self, input_filepath, timestamp="00:00:15"):
        output_image_path = str(Path(self.temp_path) / "video_frame.png")

        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            timestamp,  # Buscamos el tiempo exacto (antes del input es más rápido)
            "-i",
            input_filepath,  # Entrada de video
            "-frames:v",
            "1",  # Solo extraer 1 frame
            "-q:v",
            "5",  # Calidad alta (2-5 es ideal para JPEG)
            output_image_path,  # Ruta de salida (ej: frame.jpg o frame.png)
        ]

        try:
            print(f"Capturando frame en {timestamp}...")
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Imagen guardada en: {output_image_path}")
            return output_image_path
        except subprocess.CalledProcessError as e:
            print(f"Error al capturar el frame: {e}")


    def _generate_banner_from_skia(self, text: str, font_path: str):
        # --- CONFIGURACIÓN PARAMETRIZADA ---
        conf = {
            "width": 1100,
            "height": 320,
            "padding": 60,
            "font_size": 90,
            "line_spacing": 1.1,      # Multiplicador de altura de línea
            "letter_spacing": 0.05,   # % adicional del tamaño de fuente (Skia usa tracking)
            "font_color": "#E0E0E0",
            # Puedes usar un Hex (#000000) o el string del degradado
            "background": "linear-gradient(-225deg, #FF3CAC 0%, #562B7C 52%, #2B86C5 100%)"
        }

        output_path = str(Path(self.temp_path) / "banner_final.png")
        surface = skia.Surface(conf["width"], conf["height"])
        canvas = surface.getCanvas()

        # 1. RENDERIZADO DEL FONDO (Sólido o Degradado)
        paint_bg = skia.Paint(AntiAlias=True)
        
        if "linear-gradient" in conf["background"]:
            # Extraer colores y porcentajes del string
            colors_hex = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', conf["background"])
            stops = [float(s)/100 for s in re.findall(r'(\d+)%', conf["background"])]
            
            # Convertir hex a Skia Colors
            sk_colors = [skia.ColorSetARGB(255, int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)) for h in colors_hex]
            
            # Definir puntos del gradiente (aproximación del ángulo -225deg: diagonal superior derecha a inferior izquierda)
            # 1. Convertir las tuplas a objetos skia.Point
            pts = [skia.Point(conf["width"], 0), skia.Point(0, conf["height"])]
            
            # 2. Usar 'positions' en lugar de 'pos'
            paint_bg.setShader(skia.GradientShader.MakeLinear(
                points=pts,
                colors=sk_colors,
                positions=stops  # <--- Cambio clave aquí
            ))
        else:
            # Color sólido hex
            h = conf["background"].lstrip('#')
            paint_bg.setColor(skia.ColorSetARGB(255, int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)))

        canvas.drawRect(skia.Rect(0, 0, conf["width"], conf["height"]), paint_bg)

        # 2. CONFIGURACIÓN DE FUENTE Y TRACKING
        typeface = skia.Typeface.MakeFromFile(font_path)
        font = skia.Font(typeface, conf["font_size"])
        font.setSubpixel(True)
        font.setEdging(skia.Font.Edging.kAntiAlias)

        # 3. LÓGICA DE WRAPPING
        paragraphs = text.split("\n")
        final_lines = []
        max_text_width = conf["width"] - (conf["padding"] * 2)

        for paragraph in paragraphs:
            words = paragraph.split(" ")
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                # Calculamos ancho incluyendo el letter_spacing manual
                text_width = font.measureText(test_line) + (len(test_line) * conf["font_size"] * conf["letter_spacing"])
                
                if text_width > max_text_width and current_line:
                    final_lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            final_lines.append(current_line)

        # 4. DIBUJAR TEXTO
        h_color = conf["font_color"].lstrip('#')
        paint_text = skia.Paint(
            Color=skia.ColorSetARGB(255, int(h_color[0:2],16), int(h_color[2:4],16), int(h_color[4:6],16)),
            AntiAlias=True
        )

        line_height = conf["font_size"] * conf["line_spacing"]
        total_text_height = len(final_lines) * line_height
        start_y = (conf["height"] / 2) - (total_text_height / 2) + (conf["font_size"] * 0.75)

        for i, line in enumerate(final_lines):
            # Calculamos el ancho de línea para centrar horizontalmente
            line_width = font.measureText(line) + (len(line) * conf["font_size"] * conf["letter_spacing"])
            x_base = (conf["width"] - line_width) / 2
            y = start_y + (i * line_height)
            
            # Para aplicar letter_spacing en Skia drawString, dibujamos letra por letra 
            # o usamos TextBlob. Por simplicidad y control, ajustamos el X de cada línea.
            canvas.drawSimpleText(line, x_base, y, font, paint_text)

        # 5. GUARDAR
        image = surface.makeImageSnapshot()
        image.save(output_path, skia.kPNG)

        return "banner_final.png"

    def _generate_social_banner(self, main_text: str, sub_text: str, font_path: str):
        # --- CONFIGURACIÓN ESTILO "FARANDULEAN" ---
        conf = {
            "width": 1080,
            "height": 500,  # Un poco más alto para las capas
            "font_size_main": 85,
            "font_size_sub": 70,
            "color_bg_back": "#1C1A19", # Amarillo
            "color_bg_front": "#3D3A38", # Fucsia/Rosa
            "color_bg_tag": "#FFFFFF",   # Blanco
            "font_color_main": "#FFFFFF",
            "font_color_sub": "#000000",
        }

        output_path = str(Path(self.temp_path) / "banner_style_f.png")
        surface = skia.Surface(conf["width"], conf["height"])
        canvas = surface.getCanvas()

        # Tipografía
        typeface = skia.Typeface.MakeFromFile(font_path)
        shadow_filter = skia.ImageFilters.DropShadow(
            dx=8, 
            dy=8, 
            sigmaX=12, 
            sigmaY=12, 
            color=skia.ColorSetARGB(150, 0, 0, 0) # Negro con 150 de opacidad
        )

        # 1. DIBUJAR CAPA AMARILLA (FONDO DESFASADO)
        paint_yellow = skia.Paint(Color=self._hex_to_skia(conf["color_bg_back"]), AntiAlias=True, ImageFilter=shadow_filter) # <--- AQUÍ ESTÁ EL TRUCO)
        rect_yellow = skia.Rect.MakeXYWH(100, 100, 880, 280)
        canvas.drawRoundRect(rect_yellow, 40, 40, paint_yellow)

        # 2. DIBUJAR CAPA FUCSIA (PRINCIPAL)
        paint_pink = skia.Paint(Color=self._hex_to_skia(conf["color_bg_front"]), AntiAlias=True)
        # Un poco más a la izquierda y arriba para el efecto de profundidad
        rect_pink = skia.Rect.MakeXYWH(80, 80, 880, 260)
        canvas.drawRoundRect(rect_pink, 30, 30, paint_pink)

        # 3. RENDERIZAR TEXTO PRINCIPAL (WRAP)
        font_main = skia.Font(typeface, conf["font_size_main"])
        paint_text_main = skia.Paint(Color=self._hex_to_skia(conf["font_color_main"]), AntiAlias=True)
        
        # Lógica de wrap simplificada para el bloque rosa
        words = main_text.upper().split(" ")
        lines = []
        curr = ""
        for w in words:
            if font_main.measureText(f"{curr} {w}") < 800:
                curr = f"{curr} {w}".strip()
            else:
                lines.append(curr)
                curr = w
        lines.append(curr)

        line_h = conf["font_size_main"] * 1.1
        for i, line in enumerate(lines):
            w_text = font_main.measureText(line)
            # Centrado dentro del rect rosa (80 + 880/2)
            x = 80 + (880 - w_text) / 2
            y = 180 + (i * line_h)
            canvas.drawString(line, x, y, font_main, paint_text_main)

        # 4. CAPA BLANCA "SU MAMÁ" (EL TAG INFERIOR)
        # Calculamos el ancho basado en el sub_text
        font_sub = skia.Font(typeface, conf["font_size_sub"])
        sub_w = font_sub.measureText(sub_text) + 80
        
        paint_white = skia.Paint(Color=self._hex_to_skia(conf["color_bg_tag"]), AntiAlias=True)
        # Posicionado para que "pise" el borde inferior del rosa
        rect_white = skia.Rect.MakeXYWH(
            (conf["width"] - sub_w) / 2, 
            310, # Altura donde se superpone
            sub_w, 
            100
        )
        canvas.drawRoundRect(rect_white, 20, 20, paint_white)

        # Texto del Tag
        paint_text_sub = skia.Paint(Color=self._hex_to_skia(conf["font_color_sub"]), AntiAlias=True)
        x_sub = (conf["width"] - font_sub.measureText(sub_text)) / 2
        canvas.drawString(sub_text, x_sub, 385, font_sub, paint_text_sub)

        # GUARDAR
        image = surface.makeImageSnapshot()
        image.save(output_path, skia.kPNG)
        return "banner_style_f.png"

    def _hex_to_skia(self, hex_color):
        h = hex_color.lstrip('#')
        return skia.ColorSetARGB(255, int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    def _generate_fixed_layer(self, watermark_text, hook_text, frame_filepath):
        output_png = str(Path(self.temp_path) / "temp_ui.png")
        CANVAS_SIZE = (1080, 1920)
        TEXT_FONT_PATH = str(self.font_path).replace("\\", "/")

        # Watermark
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=55,
                color="white",
                size=(460, 155),
                font=TEXT_FONT_PATH,
            )
            .with_opacity(0.5)
            .with_position((0, 5))
            .rotated(15)
        )

        # Hook text
        banner_filepath = str(Path(self.temp_path) / "banner_final.png")
        banner = (
            BasicBanner(width=1100, height=320)                   
            .build_background()    
            .with_font(TEXT_FONT_PATH)
            .with_text(hook_text)
            .save_img(banner_filepath)
        )
        #banner_filename = self._generate_banner_from_html(hook_text, TEXT_FONT_PATH)
        #banner_filename = self._generate_banner_from_skia(hook_text, TEXT_FONT_PATH)
        #banner_filename = self._generate_social_banner( hook_text,"Arturo y Hache", TEXT_FONT_PATH)
        #banner_filepath = str(Path(self.temp_path) / banner_filename)
        hook = ImageClip(banner_filepath).with_position(("center", 925))

        # Logo
        logo_path = str(Path(self.assets_path) / "emoji_comment.png")
        logo = ImageClip(logo_path).resized(width=150).with_position((860, 860))

        # Watermark 
        frame_zoom_factor = 1.6
        pos_y = 1200 # starts at, counting from top to bottom
        pos_x = -320 # starts at, counting from left to right  

        frame = (
            ImageClip(frame_filepath)
            .resized(width=int(1080 * frame_zoom_factor))
            .with_position((pos_x, pos_y))
        )

        mask_array = color_gradient(
            frame.size, p1=(0, 100), p2=(0, 0), color_1=0, color_2=1, shape="linear"
        )
        mask_clip = ImageClip(mask_array, is_mask=True)
        frame_ = frame.with_mask(mask_clip)

        # Componemos y guardamos UN SOLO FRAME
        ui_composite = CompositeVideoClip(
            [watermark, frame, hook], size=CANVAS_SIZE, bg_color=None
        )
        ui_composite.save_frame(output_png, t=0)
        return output_png

    def _generate_banner_from_html(self, text: str, font_path: str):
        output_dir = self.temp_path

        texto_html = text.replace("\n", "<br>")

        hti = Html2Image(
            size=(1200, 600),
            custom_flags=[
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--disable-direct-composition",
                "--log-level=3",
                "--default-background-color=00000000",
            ],
            keep_temp_files=True,
            temp_path=output_dir,
        )

        css = f"""
        @font-face {{
            font-family: 'MontserratLocal';
            src: url('file:///{font_path}');
        }}

        body {{
            background: transparent !important; 
            margin: 0; 
            padding: 0;
            display: block; 
            overflow: hidden;
        }}

        .banner {{
            background: black;
            display: block; 
            
            /* Dimensiones fijas obligatorias */
            width: 1100px; 
            height: 320px; 
            
            /* Centrado horizontal usando márgenes */
            margin: 0 auto; 
            
            /* Centrado interno del texto */
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
            box-sizing: border-box; /* Importante para que el padding no sume al tamaño */
            padding: 50px;
        }}

        h1 {{
            color: #E0E0E0;
            font-family: 'MontserratLocal', sans-serif;
            font-size: 100px; 
            font-weight: 900;
            margin: 0;
            line-height: 1;
            letter-spacing: 5px;
            text-shadow: 0px 1px 2px rgba(0,0,0,0.2)
        }}
        """

        # Usamos la variable texto_html ya procesada
        html = f'<div class="banner"><h1>{texto_html}</h1></div>'

        hti.output_path = output_dir
        output_name = "banner_final.png"
        hti.screenshot(html_str=html, css_str=css, save_as=output_name)

        return output_name

    def _assemble(self, video_input, ui_png, video_output, debug=False):
        salida_imagen = str(Path(self.temp_path) / "debug_frame.png")
        salida_video = str(Path(self.output_path) / f"{video_output}_produced.mp4")
        if debug:
            print("DEBUG MODE: Generating one debug frame...")
            # Comando optimizado solo para extraer 1 imagen
            ffmpeg_cmd = [
                "ffmpeg",
                "-loglevel",
                "error",
                "-stats",
                "-y",
                "-ss",
                "00:00:01",  # Salta al segundo 1 (rápido)
                "-i",
                video_input,
                "-i",
                ui_png,
                "-filter_complex",
                "[0:v][1:v]overlay=0:0",
                "-frames:v",
                "1",  # Solo un frame
                "-q:v",
                "2",  # Alta calidad de imagen
                salida_imagen,  # Salida como imagen
            ]

            subprocess.run(ffmpeg_cmd, check=True)
            return salida_imagen
        else:
            print("PRODUCTION MODE: Assemble full video...")
            # Tu comando original de alto rendimiento
            ffmpeg_cmd = [
                "ffmpeg",
                "-loglevel",
                "error",
                "-stats",
                "-y",
                "-i",
                video_input,
                "-i",
                ui_png,
                "-filter_complex",
                "[0:v][1:v]overlay=0:0",
                "-c:v",
                "hevc_amf",
                "-quality",
                "0",
                "-rc",
                "cbr",
                "-b:v",
                "15M",
                "-c:a",
                "copy",
                salida_video,
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            return salida_video


class VideoBuilderV1:
    """
    First version of video builder, with zoomed video, 
    watermark text, simple comment emoji and text.
    Original the font used was cascadiacode.ttf.
    """
    def __init__(
        self,
        output_path: str,
        temp_path: str,
        font_path: str,
        assets_path: str,
    ):
        self.output_path = output_path
        self.temp_path = temp_path
        self.font_path = font_path
        self.assets_path = assets_path

    def build(
        self,
        input_filepath: str,
        file_id: str,
        watermark_text: str,
        hook_text: str,
        debug_video_frame: str,
    ):
        hook_text_cleaned = hook_text.replace(r"\n", "\n")

        # fmt: off
        resized_filepath     = self._resize_video_segment(input_filepath, file_id)
        fixed_layer_filepath = self._generate_fixed_layer(watermark_text, hook_text_cleaned)
        result_path          = self._assemble(resized_filepath, fixed_layer_filepath, file_id, debug_video_frame)
        # fmt: on
        return result_path

    def _resize_video_segment(self, input_filepath: str, file_id: str):
        resized_filepath = str(Path(self.temp_path) / f"{file_id}_segment_resized.mp4")
        resized_file_exists = Path(resized_filepath).is_file()

        if not resized_file_exists:
            print("Resized file doesnt exists. Start resizing...")
            try:
                POS_Y = 180
                # Variables de control
                CANVAS_W, CANVAS_H = 1080, 1920
                FACTOR = 1.53  # Tu 1.5x vital
                TARGET_W = int(CANVAS_W * FACTOR)  # 1620px

                safe_filter = (
                    # 1. Escalamos el VIDEO para que el ancho sea 1620.
                    # La altura se ajusta sola (-1) para no achatar.
                    f"scale={TARGET_W}:-1,"
                    # 2. Forzamos que los píxeles sean cuadrados.
                    "setsar=1:1,"
                    # 3. CORTAMOS el video al ancho del lienzo (1080).
                    # Esto elimina los bordes laterales que sobran por el zoom (el overflow).
                    # 'ih' mantiene la altura que resultó del escalado anterior.
                    f"crop={CANVAS_W}:ih,"
                    # 4. Ponemos el video en el lienzo vertical.
                    # Ahora 'iw' es exactamente 1080, así que no habrá error.
                    f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black"
                )
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-stats",
                    "-i",
                    input_filepath,
                    "-vf",
                    safe_filter,
                    "-c:v",
                    "h264_amf",
                    "-rc",
                    "cbr",
                    "-b:v",
                    "18M",  # Subimos a 18M para que el zoom no pierda nitidez
                    "-quality",
                    "quality",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    resized_filepath,
                ]
                print("Resizing video for mobile canvas...")
                subprocess.run(ffmpeg_cmd, check=True)

                print(f"Resizing successful with file: {resized_filepath}")
                return resized_filepath
            except subprocess.CalledProcessError as e:
                print(f"Error while resizing : {e}")
                raise
        else:
            print("Resized file exists. Skipping resizing...")
            return resized_filepath

    def _generate_fixed_layer(self, watermark_text, hook_text):
        output_png = str(Path(self.temp_path) / "temp_ui.png")
        CANVAS_SIZE = (1080, 1920)
        TEXT_FONT_PATH = self.font_path

        hook = TextClip(
            text=hook_text,
            font_size=100,
            color="white",
            bg_color="black",
            method="caption",
            size=(920, 350),
            text_align="center",
            vertical_align="center",
            font=TEXT_FONT_PATH,
        ).with_position(("center", 1150))

        # Watermark
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=55,
                color="gray",
                size=(460, 155),
                font=TEXT_FONT_PATH,
            )
            .with_position((50, 15))
            .rotated(15)
        )

        # Logo
        logo_path = str(Path(self.assets_path) / "emoji_comment.png")
        logo = ImageClip(logo_path).resized(width=150).with_position((860, 1035))

        # Componemos y guardamos UN SOLO FRAME
        ui_composite = CompositeVideoClip(
            [hook, watermark, logo], size=CANVAS_SIZE, bg_color=None
        )

        ui_composite.save_frame(output_png, t=0)
        return output_png

    def _assemble(self, video_input, ui_png, video_output, debug=False):
        salida_imagen = str(Path(self.temp_path) / "debug_frame.png")
        salida_video = str(Path(self.output_path) / f"{video_output}.mp4")
        if debug:
            print("DEBUG MODE: Generating one debug frame...")
            # Comando optimizado solo para extraer 1 imagen
            ffmpeg_cmd = [
                "ffmpeg",
                "-loglevel",
                "error",
                "-stats",
                "-y",
                "-ss",
                "00:00:01",  # Salta al segundo 1 (rápido)
                "-i",
                video_input,
                "-i",
                ui_png,
                "-filter_complex",
                "[0:v][1:v]overlay=0:0",
                "-frames:v",
                "1",  # Solo un frame
                "-q:v",
                "2",  # Alta calidad de imagen
                salida_imagen,  # Salida como imagen
            ]

            subprocess.run(ffmpeg_cmd, check=True)
            return salida_imagen
        else:
            print("PRODUCTION MODE: Assemble full video...")
            # Tu comando original de alto rendimiento
            ffmpeg_cmd = [
                "ffmpeg",
                "-loglevel",
                "error",
                "-stats",
                "-y",
                "-i",
                video_input,
                "-i",
                ui_png,
                "-filter_complex",
                "[0:v][1:v]overlay=0:0",
                "-c:v",
                "hevc_amf",
                "-quality",
                "0",
                "-rc",
                "cbr",
                "-b:v",
                "15M",
                "-c:a",
                "copy",
                salida_video,
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            return salida_video
