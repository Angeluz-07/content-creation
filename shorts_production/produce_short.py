from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, ColorClip

def producir_short(config):
    # Configuraciones base
    CANVAS_SIZE = (1080, 1920)
    FUENTE_PATH = "C:/Windows/Fonts/CascadiaCode.ttf"

    # 1. CARGA DEL VIDEO (Ya viene con el lienzo y posición de FFmpeg)
    clip_raw = VideoFileClip(config["input_video"])
    duracion = clip_raw.duration

    # 2. CREACIÓN DE ELEMENTOS DE INTERFAZ (UI)
    hook_clip = TextClip(
        text=config['hook_text'], font_size=100, color='white', bg_color='black',
        method='caption', size=(920, 350), text_align='center',
        vertical_align='center', font=FUENTE_PATH
    ).with_duration(duracion).with_position(("center", 1150))

    watermark = TextClip(
        text="@e", font_size=55, color='gray',
        size=(460, 155), font=FUENTE_PATH
    ).with_duration(duracion).with_position((50, 15)).rotated(15)

    logo_final = ImageClip("emoji_comment.png") \
                .resized(width=150) \
                .with_duration(duracion) \
                .with_position((800, 1035))

    # 3. APLANADO DE UI (Optimización de rendimiento)
    ui_composite = CompositeVideoClip([hook_clip, watermark, logo_final], size=CANVAS_SIZE)
    
    # Extraemos el frame y su transparencia
    ui_estatica = ImageClip(ui_composite.get_frame(0))
    ui_estatica.mask = ImageClip(ui_composite.mask.get_frame(0), is_mask=True)
    ui_estatica = ui_estatica.with_duration(duracion)

    # 4. COMPOSICIÓN FINAL
    # Al no poner .with_position(), ambos clips se alinean al (0,0)
    final_video = CompositeVideoClip(
        [clip_raw, ui_estatica],
        size=CANVAS_SIZE
    )

    # 5. RENDERIZADO
    if config.get('debug_mode'):
        final_video.save_frame("debug_final.png", t=2)
    else:
        final_video.write_videofile(
            config['output_name'], 
            fps=30, 
            codec="hevc_amf", 
            audio_codec="aac",
            # IMPORTANTE: Seteamos el preset aquí, pero con valor numérico 
            # para que el driver de AMD no intente "evaluar" texto.
            preset="0", 
            ffmpeg_params=[
                "-pix_fmt", "yuv420p",
                "-rc", "vbr_latency",
                "-quality", "speed" # Intentamos pasarlo aquí si el preset falla
            ]
        )
    
config = {
    "input_video": "test.mp4",
    "hook_text": " \n Desclasifica \n su pasado",
    "debug_mode": False,
    "output_name": "output_test.mp4"
}

import time

start_time = time.perf_counter()

# === Your code goes here ===
producir_short(config)
# ===========================

end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")