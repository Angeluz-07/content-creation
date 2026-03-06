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
    
    ANCHO_HOOK = 920  # Dejamos margen a los lados (1080 - 160)
    ALTO_HOOK = 350   # Altura fija para dar "aire" arriba y abajo

    hook_clip = TextClip(
        text=config['hook_text'],
        font_size=100,
        color='white',
        bg_color='black',
        method='caption',
        size=(ANCHO_HOOK, ALTO_HOOK), # Altura fija en lugar de None
        text_align='center',          # Centrado horizontal
        vertical_align='center',      # Centrado vertical dentro de la caja
    ).with_duration(clip_raw.duration)

    # 2. Posicionamiento
    # Al tener una altura de 350, si lo pones en Y=1200, 
    # el borde inferior llegará a 1550, dejando espacio libre abajo.
    posicion_y_hook = 1150 

    hook_final = hook_clip.with_position(("center", posicion_y_hook))

    # 5. Marca de Agua
    watermark = TextClip(
        text="@e",
        font_size=60,
        color='gray',
        size=(350, 150), # Altura fija en lugar de None
    ).with_duration(clip_raw.duration).with_position((50, 15)).rotated(15)

    # 6. Composición
    # Colocamos las piezas sobre el fondo.
    final_video = CompositeVideoClip(
        [fondo, video_estirado.with_position(posicion_video), hook_final, watermark],
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
    "hook_text": " \n Desclasifica \n su pasado",
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