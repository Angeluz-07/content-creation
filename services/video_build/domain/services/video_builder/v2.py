import subprocess
from pathlib import Path
from moviepy import TextClip, CompositeVideoClip, ImageClip
from moviepy.video.tools.drawing import color_gradient
from domain.services.banner import BasicBanner, StackedBanner
from pathlib import Path

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
    ):
        self.output_path = output_path
        self.temp_path = temp_path

    def build(
        self,
        params,
    ):

        # fmt: off
        input_filepath    = params["input_filepath"]
        file_id           = Path(input_filepath).stem   
        watermark_text    = params["watermark_text"]
        output_filename   = params["output_filename"]
        debug_video_frame = params["debug_video_frame"]
        hook_text         = params["hook_text"]
        hook_text_cleaned = hook_text.replace(r"\n", "\n")
        frame_ts          = params["frame_ts"]
        font_path         = params["font_path"]
        force_resize      = params["force_resize"]

        resized_filepath     = self._resize_video_segment(input_filepath, file_id, force_resize)
        frame_filepath       = self._get_video_frame(input_filepath, frame_ts)
        fixed_layer_filepath = self._generate_fixed_layer(watermark_text, hook_text_cleaned, font_path, frame_filepath)
        result_path          = self._assemble(resized_filepath, fixed_layer_filepath, output_filename, debug_video_frame)
        # fmt: on
        return result_path

    def _resize_video_segment(
        self, input_filepath: str, file_id: str, force_resize: bool
    ):
        resized_filepath = str(Path(self.temp_path) / f"{file_id}_resized.mp4")
        resized_file_exists = Path(resized_filepath).is_file()

        if force_resize or not resized_file_exists:
            print("Resized file doesnt exists. Start resizing...")
            try:
                POS_Y = 0
                CANVAS_W, CANVAS_H = 1080, 1920
                ZOOM_FACTOR = 1.53
                TARGET_W = int(CANVAS_W * ZOOM_FACTOR)  # 1620px

                # fmt: off
                safe_filter = (
                    f"scale={TARGET_W}:-1,"
                    "setsar=1:1,"
                    f"crop={CANVAS_W}:ih,"
                    f"pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black"
                )
                # for portability(docker usage) we use cpu encoders.
                # we trade off processing time for portability
                encoders = [
                    "-c:v", "libx264",
                    "-crf", "21",
                    "-preset", "fast"
                ]
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-loglevel","error",
                    "-stats",
                    "-i", input_filepath,
                    "-vf", safe_filter,
                    *encoders,
                    "-pix_fmt", "yuv420p", # ensures compatibility
                    "-c:a", "copy",
                    resized_filepath,
                ]
                # fmt: on
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
        # fmt: off
        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel","error",
            "-y",
            "-ss", timestamp,  # Buscamos el tiempo exacto (antes del input es más rápido)
            "-i", input_filepath,  # Entrada de video
            "-frames:v", "1",  # Solo extraer 1 frame
            output_image_path,  # Ruta de salida (ej: frame.jpg o frame.png)
        ]
        # fmt: on
        try:
            print(f"Capturando frame en {timestamp}...")
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Imagen guardada en: {output_image_path}")
            return output_image_path
        except subprocess.CalledProcessError as e:
            print(f"Error al capturar el frame: {e}")

    def _generate_fixed_layer(
        self, watermark_text, hook_text, font_path, frame_filepath
    ):
        output_png = str(Path(self.temp_path) / "temp_ui.png")
        CANVAS_SIZE = (1080, 1920)

        # Watermark
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=55,
                color="white",
                size=(460, 155),
                font=font_path,
            )
            .with_opacity(0.5)
            .with_position((0, 5))
            .rotated(15)
        )

        # Hook text
        banner_filepath = str(Path(self.temp_path) / "banner_final.png")
        banner = (
            BasicBanner(width=1100, height=320, font_path=font_path, text=hook_text)
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

        frame_zoom_factor = 1.3
        pos_y = 1200  # starts at, counting from top to bottom
        pos_x = -120  # starts at, counting from left to right

        frame = (
            ImageClip(frame_filepath)
            .resized(width=int(1080 * frame_zoom_factor))
            .with_position((pos_x, pos_y))
        )

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
            # fmt: off
            ffmpeg_cmd = [
                "ffmpeg",
                "-loglevel","error",
                "-stats","-y",
                "-ss", "00:00:01",  # Salta al segundo 1 (rápido)
                "-i", video_input,
                "-i", ui_png,
                "-filter_complex", "[0:v][1:v]overlay=0:0",
                "-frames:v", "1",
                "-q:v", "2",  # Alta calidad de imagen
                salida_imagen,  # Salida como imagen
            ]
            # fmt: on
            subprocess.run(ffmpeg_cmd, check=True)
            return salida_imagen
        else:
            print("PRODUCTION MODE: Assemble full video...")
            # fmt: off
            # for portability(docker usage) we use cpu encoders.
            # we trade off processing time for portability
            encoders = [
                "-c:v", "libx264",
                "-crf", "21",
                "-preset", "fast"
            ]
            ffmpeg_cmd = [
                "ffmpeg",
                "-loglevel", "error",
                "-stats",
                "-y",
                "-i", video_input,
                "-i", ui_png,
                "-filter_complex", "[0:v][1:v]overlay=0:0",
                *encoders,
                "-pix_fmt", "yuv420p",
                "-c:a","copy",
                salida_video,
            ]
            # fmt: off
            subprocess.run(ffmpeg_cmd, check=True)
            return salida_video
