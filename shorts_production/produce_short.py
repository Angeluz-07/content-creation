from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, ColorClip


def generar_capa_ui(config, output_png="temp/temp_ui.png"):
    CANVAS_SIZE = (1080, 1920)
    FUENTE_PATH = "C:/Windows/Fonts/CascadiaCode.ttf"

    # Hook
    hook = TextClip(
        text=config['hook_text'], font_size=100, color='white', bg_color='black',
        method='caption', size=(920, 350), text_align='center',
        vertical_align='center', font=FUENTE_PATH
    ).with_position(("center", 1150))

    # Watermark
    watermark = TextClip(
        text="@elTarrinero", font_size=55, color='gray',
        size=(460, 155), font=FUENTE_PATH
    ).with_position((50, 15)).rotated(15)

    # Logo
    logo = ImageClip("assets/emoji_comment.png").resized(width=150).with_position((800, 1035))

    # Componemos y guardamos UN SOLO FRAME
    ui_composite = CompositeVideoClip([hook, watermark, logo], size=CANVAS_SIZE, bg_color=None)
    ui_composite.save_frame(output_png, t=0)
    return output_png

import subprocess

def ensamblar_final(video_input, ui_png, video_output, debug=False):
    if debug:
        print("🔍 MODO DEBUG: Generando un solo frame de prueba...")
        # Comando optimizado solo para extraer 1 imagen
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-ss', '00:00:01',            # Salta al segundo 1 (rápido)
            '-i', video_input,
            '-i', ui_png,
            '-filter_complex', '[0:v][1:v]overlay=0:0',
            '-frames:v', '1',             # Solo un frame
            '-q:v', '2',                  # Alta calidad de imagen
            'temp/debug_frame.jpg'             # Salida como imagen
        ]
    else:
        print("🚀 MODO PRODUCCIÓN: Ensamblado completo...")
        # Tu comando original de alto rendimiento
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', video_input,
            '-i', ui_png,
            '-filter_complex', '[0:v][1:v]overlay=0:0',
            '-c:v', 'hevc_amf',
            '-quality', '0',
            '-rc', 'cbr',
            '-b:v', '15M',
            '-c:a', 'copy',
            video_output
        ]

    subprocess.run(ffmpeg_cmd, check=True)

config = {
    "input_video": "temp/.mp4",
    "hook_text": " \n\"El pueblo no\n te quiere\"",
    "debug_mode": 0,
    "output_name": "output_videos/.mp4"
}

import time

start_time = time.perf_counter()

# === Your code goes here ===
#producir_short(config)
# 1. Generas la imagen una sola vez
ui_file = generar_capa_ui(config)

# 2. Unes todo con la potencia de la GPU
ensamblar_final(config["input_video"], ui_file, config["output_name"], config["debug_mode"])
# ===========================

end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")