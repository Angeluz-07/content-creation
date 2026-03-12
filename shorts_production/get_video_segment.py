import subprocess
import os

import subprocess
import subprocess
import os

import subprocess
import os

def get_segment(url, inicio, fin, nombre_salida, id):
    temp_file = f"temp/{id}_raw_download.mp4"
    
    # 1. Verificar si el archivo temporal ya existe
    if os.path.exists(temp_file):
        print(f"♻️ El archivo temporal '{temp_file}' ya existe. Saltando descarga...")
    else:
        # Descarga limpia del segmento
        ydl_opts = [
            'yt-dlp', '--quiet', '--no-warnings',
            '-f', 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/mp4',
            '--external-downloader', 'ffmpeg',
            '--external-downloader-args', f'ffmpeg_i:-ss {inicio} -to {fin}',
            url, '-o', temp_file
        ]
        try:
            print("📥 Descargando segmento de YouTube...")
            subprocess.run(ydl_opts, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en la descarga: {e}")
            return

    # 2. Procesamiento local con GPU (Filtros corregidos + AMF)
    try:
        POS_Y=180
        # Variables de control
        CANVAS_W, CANVAS_H = 1080, 1920
        FACTOR = 1.5  # Tu 1.5x vital
        TARGET_W = int(CANVAS_W * FACTOR) # 1620px

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
            'ffmpeg', '-y', '-i', temp_file,
            '-vf', safe_filter,
            '-c:v', 'h264_amf', 
            '-rc', 'cbr',
            '-b:v', '18M',         # Subimos a 18M para que el zoom no pierda nitidez
            '-quality', 'quality', 
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',     
            nombre_salida
        ]
        print("🚀 Aplicando hardware acceleration (AMF) con filtros corregidos...")
        subprocess.run(ffmpeg_cmd, check=True)
        
        print(f"✅ Proceso terminado con éxito: {nombre_salida}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error en el procesamiento de FFmpeg: {e}")

url = "https://www.youtube.com/watch?v"
inicio =  "00:09:10" 
fin = "00:10:18"
id = "tarri"

nombre_salida = f"temp/{id}_resized.mp4"
get_segment(url, inicio, fin, nombre_salida, id)