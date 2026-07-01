from pathlib import Path
from .common import run_async_subprocess, run_subprocess


class Assembler:

    def __init__(self, temp_path: str, output_path: str):
        self.temp_path = temp_path
        self.output_path = output_path

    async def run_async(
        self,
        input_filepath: str,
        ui_png: str,
        output_filename: str,
        debug: bool = False,
    ) -> str:
        """Asynchronously assemble video or generate a debug frame."""
        output_target = self.get_output_filepath(output_filename, debug)
        ffmpeg_cmd = self.get_command(input_filepath, ui_png, output_target, debug)

        print(f"{'DEBUG' if debug else 'PRODUCTION'} MODE: Assembling (Async)...")
        await run_async_subprocess(command=ffmpeg_cmd)
        return output_target

    def run(
        self,
        input_filepath: str,
        ui_png: str,
        output_filename: str,
        debug: bool = False,
    ) -> str:
        """Synchronously assemble video or generate a debug frame."""
        output_target = self.get_output_filepath(output_filename, debug)
        ffmpeg_cmd = self.get_command(input_filepath, ui_png, output_target, debug)
        print(f"{'DEBUG' if debug else 'PRODUCTION'} MODE: Assembling (Sync)...")
        run_subprocess(command=ffmpeg_cmd)
        return output_target

    def get_output_filepath(self, output_filename: str, debug: bool) -> str:
        """Resolves the definitive file output path depending on mode."""
        if debug:
            return str(Path(self.temp_path) / "debug_frame.png")
        return str(Path(self.output_path) / f"{output_filename}.mp4")

    def get_command(
        self, video_input: str, ui_png: str, target_output: str, debug: bool
    ) -> list[str]:
        """Generates the appropriate FFmpeg execution array."""
        # fmt: off
        if debug:
            command = [
                "ffmpeg", "-y",
                "-loglevel", "error",
                "-stats", "-y",
                "-ss", "00:00:01",  # Fast jump to second 1
                "-i", video_input,
                "-i", ui_png,
                "-filter_complex", "[0:v][1:v]overlay=0:0",
                "-frames:v", "1",
                "-q:v", "2",
                target_output
            ]
            return command
        else:
            encoders = [
                "-c:v", "libx264", 
                "-crf", "21",
                "-preset", "fast"
            ]
            command = [
                "ffmpeg", "-y",
                "-loglevel", "error",
                "-stats", "-y",
                "-i", video_input,
                "-i", ui_png,
                "-filter_complex", "[0:v][1:v]overlay=0:0",
                *encoders,
                "-pix_fmt", "yuv420p",
                "-c:a", "copy",
                target_output
            ]            
            return command
