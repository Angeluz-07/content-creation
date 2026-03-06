from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, ColorClip

def producir_short(config):
    # 1. Dimensiones Base (Formato Móvil 1080x1920)
    CANVAS_W = 1080
    CANVAS_H = 1920
    
    # 2. Cargar video y redimensionar
    # En lugar de zoom, lo ajustamos al ancho del canvas
    clip_raw = VideoFileClip(config["input_video"])
    video_redimensionado = clip_raw.resized(width=CANVAS_W) 
    
    # 3. Crear Fondo Negro (Lienzo)
    fondo = ColorClip(size=(CANVAS_W, CANVAS_H), color=(0, 0, 0)).with_duration(clip_raw.duration)
    
    # 4. El Hook (Evitando overflow con method='caption')
    # 'caption' ajusta el texto automáticamente al ancho dado
    hook_clip = TextClip(
        text=config['hook_text'],
        font_size=70,
        color='white',
        method='caption', # Clave para que no se corte
        size=(CANVAS_W - 100, None) # Margen de 50px a los lados
    ).with_duration(clip_raw.duration).with_position(("center", 1400)) # Posición fija abajo

    # 5. Marca de Agua
    watermark = TextClip(
        text="@tu_usuario",
        font_size=40,
        color='gray'
    ).with_duration(clip_raw.duration).with_position((CANVAS_W - 300, 50))

    # 6. Composición
    # Colocamos el video en la parte superior/media
    final_video = CompositeVideoClip(
        [fondo, video_redimensionado.with_position(("center", 200)), hook_clip, watermark],
        size=(CANVAS_W, CANVAS_H)
    )

    # 7. Renderizado (Fix para reproducción en PC)
    if config.get('debug_mode'):
        final_video.save_frame("debug_rectificado.png", t=2)
    else:
        # Agregamos pixel_format para compatibilidad universal
        final_video.write_videofile(
            config['output_name'], 
            fps=30, 
            codec="libx264", 
            audio_codec="aac",
            ffmpeg_params=["-pix_fmt", "yuv420p"] # ESTO arregla que no se vea en PC
        )
    
config = {
    "input_video": "test.mp4",
    "hook_text": "DON PUCHO Desclasifica",
    "debug_mode": True,
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