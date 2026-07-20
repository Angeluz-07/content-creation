from pathlib import Path
from src.domain.common import run_async_subprocess, run_subprocess


def get_cmd_assemble_video_and_template(
    video_input: str, target_output: str, ui_png: str, debug: bool
) -> list[str]:
    """Generates the appropriate FFmpeg execution array."""
    CANVAS_W = 720
    CANVAS_H = 1280
    POS_Y = 180  # La posición vertical donde caerá tu video recortado

    # Creamos la cadena de filtros para el filter_complex.
    # 1. Tomamos el video [0:v] y le creamos el lienzo vertical negro.
    # 2. El resultado se guarda temporalmente en la etiqueta [padded].
    # 3. Encimamos la UI [1:v] sobre [padded] en la coordenada 0,0.
    filter_spec = (
        f"[0:v]pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black[padded];"
        f"[padded][1:v]overlay=0:0"
    )

    # fmt: off
    if debug:
        command = [
            "ffmpeg", "-y",
            "-loglevel", "error",
            "-stats", "-y",
            "-ss", "00:00:01",  # Fast jump to second 1
            "-i", video_input,
            "-i", ui_png,
            "-filter_complex", filter_spec,
            "-frames:v", "1",
            "-q:v", "2",
            target_output
        ]
        return command
    else:
        encoders = [
            "-c:v", "libx264", 
            "-crf", "18",
            "-preset", "ultrafast",
            "-threads", "3"
        ]
        command = [
            "ffmpeg", "-y",
            "-loglevel", "error",
            "-stats", "-y",
            "-i", video_input,
            "-i", ui_png,
            "-filter_complex", filter_spec,
            *encoders,
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            target_output
        ]            
        return command


def assemble_video_and_template(input_path, output_path, ui_png, debug):
    ffmpeg_cmd = get_cmd_assemble_video_and_template(
        input_path, output_path, ui_png, debug
    )
    print(f"{'DEBUG' if debug else 'PRODUCTION'} MODE: Assembling (Sync)...")
    run_subprocess(command=ffmpeg_cmd)
    return output_path


async def assemble_video_and_template_async(
    input_path, output_path, ui_png, debug
) -> str:
    ffmpeg_cmd = get_cmd_assemble_video_and_template(
        input_path, output_path, ui_png, debug
    )

    print(f"{'DEBUG' if debug else 'PRODUCTION'} MODE: Assembling (Async)...")
    await run_async_subprocess(command=ffmpeg_cmd)
    return output_path
