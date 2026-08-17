from pathlib import Path
from src.domain.common import run_async_subprocess, run_subprocess


def get_cmd_assemble_video_and_template2(
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
        base_dir = Path(target_output).parent.parent
        target_output = str(base_dir / "temp" / "debug_frame.png")
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

# todo: improve, split speeding from assembling
def get_cmd_assemble_video_and_template(
    video_input: str,
    target_output: str,
    ui_png: str,
    debug: bool,
    temp_dir: Path | str,
    speed: float = 1.3,
) -> list[str]:
    """Generates the appropriate FFmpeg execution array."""
    CANVAS_W = 720
    CANVAS_H = 1280
    POS_Y = 180  # La posición vertical donde caerá tu video recortado

    # fmt: off
    if debug:
        # En modo debug no aceleramos audio ni requerimos reencodar nada pesado
        filter_spec = (
            f"[0:v]pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black[padded];"
            f"[padded][1:v]overlay=0:0"
        )
        target_output = Path(temp_dir)/ "debug_frame.png"
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
        # Modificamos filter_spec para acelerar video (setpts) y audio (atempo)
        filter_spec = (
            f"[0:v]pad={CANVAS_W}:{CANVAS_H}:(ow-iw)/2:{POS_Y}:black,"
            f"setpts=PTS/{speed}[padded_fast];"
            f"[padded_fast][1:v]overlay=0:0[v_out];"
            f"[0:a]atempo={speed}[a_out]"
        )
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
            "-map", "[v_out]",  # Mapeamos explícitamente el video procesado
            "-map", "[a_out]",  # Mapeamos explícitamente el audio acelerado
            *encoders,
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",      # Cambiado de 'copy' a 'aac' porque modificamos la velocidad del audio
            target_output
        ]            
        return command


async def assemble_video_and_template(input_path, output_path, ui_png, debug, temp_dir) -> str:
    ffmpeg_cmd = get_cmd_assemble_video_and_template(
        input_path, output_path, ui_png, debug, temp_dir
    )

    print(f"{'DEBUG' if debug else 'PRODUCTION'} MODE: Assembling (Async)...")
    await run_async_subprocess(command=ffmpeg_cmd)
    return output_path
