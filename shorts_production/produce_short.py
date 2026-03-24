from moviepy import TextClip, CompositeVideoClip, ImageClip
import subprocess
import os
import time
import json
from pathlib import Path
from download_video_segment import download_segment_from_yt


def get_segment(url, inicio, fin, force_download, id):
    temp_file = f"temp/{id}_segment_raw_download.mp4"
    file_doesnt_exist = not Path(temp_file).is_file()

    if file_doesnt_exist:
        download_segment_from_yt(inicio, fin, url, temp_file)
    elif force_download:
        file_to_remove = Path(temp_file)
        file_to_remove.unlink(missing_ok=True)  # delete file
        download_segment_from_yt(inicio, fin, url, temp_file)
    else:
        print(
            f"Raw file exists & force_download={force_download}, skipping raw download..."
        )

    resized_file = f"temp/{id}_segment_resized.mp4"
    resized_file_exists = Path(resized_file).is_file()

    if not resized_file_exists:
        # 2. Procesamiento local con GPU (Filtros corregidos + AMF)
        try:
            POS_Y = 180
            # Variables de control
            CANVAS_W, CANVAS_H = 1080, 1920
            FACTOR = 1.5  # Tu 1.5x vital
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
                temp_file,
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
                resized_file,
            ]
            print("Resizing video for mobile canvas...")
            subprocess.run(ffmpeg_cmd, check=True)

            print(f"Resizing successful with file: {resized_file}")
            return resized_file
        except subprocess.CalledProcessError as e:
            print(f"Error while resizing : {e}")
    else:
        print("Resized file exists. Skipping resizing...")
        return resized_file


def generar_capa_ui(config, hook_text, output_png="temp/temp_ui.png"):
    CANVAS_SIZE = (1080, 1920)
    FUENTE_PATH = "C:/Windows/Fonts/CascadiaCode.ttf"

    # Hook
    hook = TextClip(
        text=hook_text,
        font_size=100,
        color="white",
        bg_color="black",
        method="caption",
        size=(920, 350),
        text_align="center",
        vertical_align="center",
        font=FUENTE_PATH,
    ).with_position(("center", 1150))

    # Watermark
    watermark = (
        TextClip(
            text=config["watermark_text"],
            font_size=55,
            color="gray",
            size=(460, 155),
            font=FUENTE_PATH,
        )
        .with_position((50, 15))
        .rotated(15)
    )

    # Logo
    logo = (
        ImageClip("assets/emoji_comment.png")
        .resized(width=150)
        .with_position((800, 1035))
    )

    # Componemos y guardamos UN SOLO FRAME
    ui_composite = CompositeVideoClip(
        [hook, watermark], size=CANVAS_SIZE, bg_color=None
    )
    ui_composite.save_frame(output_png, t=0)
    return output_png


def ensamblar_final(video_input, ui_png, video_output, debug=False):
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
            "temp/debug_frame.jpg",  # Salida como imagen
        ]
    else:
        print("PRODUCTION MODE: Ensemble full video...")
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
            video_output,
        ]

    subprocess.run(ffmpeg_cmd, check=True)


with open("config.json", "r", encoding="utf-8") as file:
    configs = json.load(file)
    config = configs[0]  # get most recent config to work with

SEGMENT_INDEX = -1


start_time = time.perf_counter()
# === Your code goes here ===
resized_filepath = get_segment(
    config["url"],
    config["segments"][SEGMENT_INDEX]["start_segment"],
    config["segments"][SEGMENT_INDEX]["end_segment"],
    config["force_download"],
    id=Path(config["segments"][SEGMENT_INDEX]["output_name"]).stem.split("_")[-1],
)
# ===========================
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")

#####

start_time = time.perf_counter()

# === Your code goes here ===
ui_file = generar_capa_ui(config, config["segments"][SEGMENT_INDEX]["hook_text"])
ensamblar_final(
    resized_filepath,
    ui_file,
    config["segments"][SEGMENT_INDEX]["output_name"],
    config["debug_video_frame"],
)
# ===========================

end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")
