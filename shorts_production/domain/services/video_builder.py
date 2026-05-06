import subprocess
from pathlib import Path
from moviepy import TextClip, CompositeVideoClip, ImageClip
from moviepy.video.tools.drawing import color_gradient

from html2image import Html2Image


class VideoBuilder:

    def __init__(
        self, output_path: str, font_path: str, assets_path: str, output_path_: str
    ):
        self.output_path = output_path
        self.font_path = font_path
        self.assets_path = assets_path
        self.output_path_ = output_path_

    def _resize_video_segment(self, input_filepath: str, file_id: str):
        resized_filepath = str(
            Path(self.output_path) / f"{file_id}_segment_resized.mp4"
        )
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

    def _get_video_frame(self, input_filepath, timestamp="00:00:12"):
        output_image_path = str(Path(self.output_path) / "video_frame.png")

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

    def _generate_fixed_layer(self, watermark_text, hook_text, frame_filepath):
        output_png = str(Path(self.output_path) / "temp_ui.png")
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
        banner_filename = self._generate_banner_from_html(hook_text, TEXT_FONT_PATH)
        banner_filepath = str(Path(self.output_path) / banner_filename)
        hook = ImageClip(banner_filepath).with_position(("center", 925))

        # Logo
        logo_path = str(Path(self.assets_path) / "emoji_comment.png")
        logo = ImageClip(logo_path).resized(width=150).with_position((860, 860))

        # Watermark
        frame = (
            ImageClip(frame_filepath)
            .resized(width=int(1080 * 1.9))
            .with_position(("center", 1220))
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
        output_dir = self.output_path

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
            line-height: 0.9;
            letter-spacing: 10px;
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
        salida_imagen = str(Path(self.output_path) / "debug_frame.png")
        salida_video = str(Path(self.output_path_) / f"{video_output}.mp4")
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
