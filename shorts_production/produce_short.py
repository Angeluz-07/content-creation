from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, ColorClip

def producir_short(config):
    # 1. Dimensiones Base (Formato Móvil 1080x1920)
    CANVAS_W = 1080
    CANVAS_H = 1920
    
    # 2. Cargar video y aplicar estiramiento NO UNIFORME
    clip_raw = VideoFileClip(config["input_video"])
    
    # --- AJUSTE AQUÍ ---
    # Queremos que el ancho siga siendo el del lienzo.
    nuevo_ancho = CANVAS_W
    # Supongamos que queremos estirarlo un 20% más hacia abajo de su altura original redimensionada.
    # Primero calculamos la altura que tendría si fuera un resize uniforme:
    altura_uniforme = clip_raw.h * (CANVAS_W / clip_raw.w)
    # Ahora aplicamos el estiramiento vertical (ej. 1.2 es un 20% más de alto)
    factor_estiramiento_v = 1.5 
    nueva_altura = int(altura_uniforme * factor_estiramiento_v)
    
    # Aplicamos el resize no uniforme pasando un diccionario
    video_estirado = clip_raw.resized(width=int(nuevo_ancho), height=int(nueva_altura))
    
    # La posición inicial vertical (Y=200) está correcta según me dices,
    # así que el video crecerá hacia abajo desde ese punto.
    posicion_video = ("center", 180) 

    # 3. Crear Fondo Negro (Lienzo)
    fondo = ColorClip(size=(CANVAS_W, CANVAS_H), color=(0, 0, 0)).with_duration(clip_raw.duration)
    
    # ... (Resto del código de TextClips para Hook y Marca de Agua sigue igual) ...
    # El Hook lo movemos un poco más abajo si el video ahora ocupa más espacio
    hook_clip = TextClip(
        text=config['hook_text'],
        font_size=70,
        color='white',
        method='caption',
        size=(CANVAS_W - 100, None)
    ).with_duration(clip_raw.duration).with_position(("center", 1600)) # Ajustado hacia abajo

    # 5. Marca de Agua
    watermark = TextClip(
        text="@tu_usuario",
        font_size=40,
        color='gray'
    ).with_duration(clip_raw.duration).with_position((CANVAS_W - 300, 50))

    # 6. Composición
    # Colocamos las piezas sobre el fondo.
    final_video = CompositeVideoClip(
        [fondo, video_estirado.with_position(posicion_video), hook_clip, watermark],
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