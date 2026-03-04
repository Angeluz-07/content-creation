import subprocess
import os

def get_segment(url, inicio, fin, nombre_salida):
    # Definimos los argumentos para que parezca una petición humana
    ydl_opts = [
        'yt-dlp',
        '--quiet', '--no-warnings',
        '--format', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        '--external-downloader', 'ffmpeg',
        # Argumentos críticos para descargar solo el fragmento:
        '--external-downloader-args', f'ffmpeg_i:-ss {inicio} -to {fin}',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        url,
        '-o', nombre_salida
    ]
    
    try:
        subprocess.run(ydl_opts, check=True)
        print(f"✅ Clip saved: {nombre_salida}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")

url = ""
inicio =  "00:56:06" 
fin = "00:57:33"
nombre_salida = "test.mp4"
get_segment(url, inicio, fin, nombre_salida)
# Ejemplo de uso:
# descargar_segmento_seguro("https://www.youtube.com/watch?v=...", "00:45:00", "00:46:30", "clip_temp.mp4")