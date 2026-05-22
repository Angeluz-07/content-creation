import subprocess
from pathlib import Path
from moviepy import TextClip, CompositeVideoClip, ImageClip
from moviepy.video.tools.drawing import color_gradient
from domain.services.banner import BasicBanner, StackedBanner
from pathlib import Path


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
        frame_ts: str,
        output_filename: str, 
    ):
        hook_text_cleaned = hook_text.replace(r"\n", "\n")

        # fmt: off
        resized_filepath     = self._resize_video_segment(input_filepath, file_id)
        frame_filepath       = self._get_video_frame(input_filepath, frame_ts)
        fixed_layer_filepath = self._generate_fixed_layer(watermark_text, hook_text_cleaned, frame_filepath)
        result_path          = self._assemble(resized_filepath, fixed_layer_filepath, output_filename, debug_video_frame)
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
            BasicBanner(
                width=1100, height=320, font_path=TEXT_FONT_PATH, text=hook_text
            )
            .render()
            .save_img(banner_filepath)
        )
        # banner = (
        #     StackedBanner(
        #         width=1080,
        #         height=500,
        #         main_text=hook_text,
        #         sub_text="Arturo y Hache",
        #         font_path=TEXT_FONT_PATH,
        #     )
        #     .render()
        #     .save_img(banner_filepath)
        # )

        hook = ImageClip(banner_filepath).with_position(("center", 925))

        # Logo
        logo_path = str(Path(self.assets_path) / "emoji_comment.png")
        logo = ImageClip(logo_path).resized(width=150).with_position((860, 860))

        # Watermark
        frame_zoom_factor = 1.3
        pos_y = 1200  # starts at, counting from top to bottom
        pos_x = -110  # starts at, counting from left to right

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

    def _assemble(self, video_input, ui_png, output_filename, debug=False):
        salida_imagen = str(Path(self.temp_path) / "debug_frame.png")
        salida_video = str(Path(self.output_path) / f"{output_filename}.mp4")
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
        output_filename: str
    ):
        hook_text_cleaned = hook_text.replace(r"\n", "\n")

        # fmt: off
        resized_filepath     = self._resize_video_segment(input_filepath, file_id)
        fixed_layer_filepath = self._generate_fixed_layer(watermark_text, hook_text_cleaned)
        result_path          = self._assemble(resized_filepath, fixed_layer_filepath, output_filename, debug_video_frame)
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

    def _assemble(self, video_input, ui_png, output_filename, debug=False):
        salida_imagen = str(Path(self.temp_path) / "debug_frame.png")
        salida_video = str(Path(self.output_path) / f"{output_filename}.mp4")
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
