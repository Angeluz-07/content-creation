from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip

def create_short(config):
    # 1. Cargar clip original
    clip = VideoFileClip(config["input_video"])
    
    # 2. Recorte para formato móvil (Vertical)
    # Ejemplo: Tomar el centro del video
    w, h = clip.size
    target_ratio = 9/16
    v_width = int(h * target_ratio)
    video_cropped = clip.cropped(x_center=w/2, width=v_width, height=h)
    
    # 1. El Hook (Letras abajo sobre fondo negro)
    txt_clip = TextClip(
        text=config['hook_text'],
        font_size=60,
        color='white',
        bg_color='black',
        size=(int(v_width), 250) # El fondo negro se define con 'size'
    ).with_duration(clip.duration).with_position(("center", "bottom"))

    # 2. La Marca de Agua (Arriba derecha)
    # Si quieres que sea más pequeña, ajusta el font_size o usa .resized()
    watermark = TextClip(
        text="@miusuario",
        font_size=30,
        color='gray'
    ).with_duration(clip.duration).with_position((int(v_width * 0.8), 20))

    # 5. Montaje Final
    final_video = CompositeVideoClip([video_cropped, txt_clip, watermark], size=(v_width, int(h)))
    
    if config.get('debug_mode'):
        final_video.save_frame("debug_position.png", t=1) # Imagen rápida de prueba
    else:
        final_video.write_videofile(config['output_name'], fps=30)
    
config = {
    "input_video": "test.mp4",
    "hook_text": "DON PUCHO Desclasifica",
    "debug_mode": True,
    "output_name": "output_test.mp4"
}

import time

start_time = time.perf_counter()

# === Your code goes here ===
create_short(config)
# ===========================

end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.4f} seconds")