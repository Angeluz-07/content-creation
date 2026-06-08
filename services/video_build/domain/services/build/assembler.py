from pathlib import Path
from domain.services.build.common import run_async_subprocess


class Assembler:

    def __init__(self, temp_path, output_path):
        self.temp_path = temp_path
        self.output_path = output_path

    async def run(self, input_filepath: str, ui_png, output_filename, debug=False):

        result_filepath = await self._assemble(
            input_filepath, ui_png, output_filename, debug
        )
        return result_filepath

    async def _assemble(self, video_input, ui_png, output_filename, debug=False):
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
            await run_async_subprocess(command=ffmpeg_cmd)
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
            await run_async_subprocess(command=ffmpeg_cmd)
            return salida_video
