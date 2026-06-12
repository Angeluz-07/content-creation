from pathlib import Path
from domain.services.common import run_async_subprocess
from domain.services.common import run_subprocess


class Extractor:

    def __init__(self, temp_path):
        self.temp_path = temp_path

    async def run_async(
        self,
        input: str,
        timestamp: str,
    ):
        output = self.get_frame_path()
        print("Capturing frame (Async)...")

        ffmpeg_cmd = self.get_comand(input, output, timestamp)

        await run_async_subprocess(command=ffmpeg_cmd)

        print(f"Capturing frame successful with file: {output}")
        return output

    def run(
        self,
        input: str,
        timestamp: str,
    ):
        output = self.get_frame_path()
        print("Capturing frame (Sync)...")

        ffmpeg_cmd = self.get_comand(input, output, timestamp)

        run_subprocess(command=ffmpeg_cmd)

        print(f"Capturing frame successful with file: {output}")
        return output

    def get_frame_path(self):
        output_image_path = str(Path(self.temp_path) / "video_frame.png")
        return output_image_path

    def get_comand(self, input, output, timestamp="00:00:01"):
        # fmt: off
        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel","error",
            "-y",
            "-ss", timestamp,  # Buscamos el tiempo exacto (antes del input es más rápido)
            "-i", input,  # Entrada de video
            "-frames:v", "1",  # Solo extraer 1 frame
            output,  # Ruta de salida (ej: frame.jpg o frame.png)
        ]
        # fmt: on
        return ffmpeg_cmd
