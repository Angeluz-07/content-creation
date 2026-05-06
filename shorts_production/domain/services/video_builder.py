from pathlib import Path
import subprocess

class VideoBuilder:
    
    def __init__(self, output_path: str):
        self.output_path = output_path

    def _resize_video_segment(self, input_filepath: str, file_id:str):
        resized_filepath = str(Path(self.output_path) / f"{file_id}_segment_resized.mp4")
        resized_file_exists = Path(resized_filepath).is_file()

        if not resized_file_exists:
            print("Resized file doesnt exists. Start resizing...")
            try:
                POS_Y = 0
                CANVAS_W, CANVAS_H = 1080, 1920
                ZOOM_FACTOR = 1.53  
                TARGET_W = int(CANVAS_W * ZOOM_FACTOR)  # 1620px

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
                    input_filepath,
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
                    resized_filepath,
                ]
                print("Resizing video for mobile canvas...")
                subprocess.run(ffmpeg_cmd, check=True)

                print(f"Resizing successful with file: {resized_filepath}")
                return resized_filepath
            except subprocess.CalledProcessError as e:
                print(f"Error while resizing : {e}")
                raise
        else:
            print("Resized file exists. Skipping resizing...")
            return resized_filepath

    def _get_video_frame(self, input_filepath, timestamp="00:00:12"):
        output_image_path = str(Path(self.output_path) / "video_frame.png")

        ffmpeg_cmd = [
            "ffmpeg",
            "-loglevel", "error",
            "-y",
            "-ss", timestamp,              # Buscamos el tiempo exacto (antes del input es más rápido)
            "-i", input_filepath,          # Entrada de video
            "-frames:v", "1",               # Solo extraer 1 frame
            "-q:v", "5",                    # Calidad alta (2-5 es ideal para JPEG)
            output_image_path              # Ruta de salida (ej: frame.jpg o frame.png)
        ]
        
        try:
            print(f"Capturando frame en {timestamp}...")
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Imagen guardada en: {output_image_path}")
            return output_image_path
        except subprocess.CalledProcessError as e:
            print(f"Error al capturar el frame: {e}")
    