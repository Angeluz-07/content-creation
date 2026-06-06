import subprocess
from pathlib import Path
from moviepy import TextClip, CompositeVideoClip, ImageClip
from moviepy.video.tools.drawing import color_gradient
from domain.services.banner import BasicBanner, StackedBanner
from pathlib import Path


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
        font_path         = params["font_path"]
        sticker_path      = params["sticker_path"]
        force_resize      = params["force_resize"]

        resized_filepath     = self._resize_video_segment(input_filepath, file_id, force_resize)
        fixed_layer_filepath = self._generate_fixed_layer(watermark_text, hook_text_cleaned, font_path, sticker_path)
        result_path          = self._assemble(resized_filepath, fixed_layer_filepath, output_filename, debug_video_frame)
        # fmt: on
        return result_path

    def _resize_video_segment(self, input_filepath: str, file_id: str, force_resize: bool):
        resized_filepath = str(Path(self.temp_path) / f"{file_id}_resized.mp4")
        resized_file_exists = Path(resized_filepath).is_file()

        if force_resize or not resized_file_exists:
            print("Resized file doesnt exists. Start resizing...")
            try:
                POS_Y = 180
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
        #logo_path = str(Path(self.assets_path) / "emoji_comment.png")
        logo = ImageClip(sticker_path).resized(width=150).with_position((860, 1035))

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
