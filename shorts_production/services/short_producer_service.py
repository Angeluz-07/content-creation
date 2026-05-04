import yt_dlp
import random
import time
import subprocess
from pathlib import Path
from dbs.interfaces import IRepository
from moviepy import TextClip, CompositeVideoClip, ImageClip

from domain.models import Config
#todo move functions to domain service


class ShortProducer:
    def __init__(self, config_repo: IRepository):
        self.config_repo = config_repo

    def run(self, config_dict):
        c = Config(**config_dict)
        print("processing", c.url)
        URL = c.url
        START_SEGMENT = c.start_segment
        END_SEGMENT = c.end_segment
        FORCE_DOWNLOAD = c.force_download
        OUTPUT_NAME = c.outname

        WATERMARK_TEXT = c.watermark_text
        HOOK_TEXT = c.hook_text.replace(r'\n', '\n') # todo improve
        DEBUG_VIDEO_FRAME = c.debug_video_frame

        resized_filepath = self.get_segment(
            URL,
            START_SEGMENT,
            END_SEGMENT,
            FORCE_DOWNLOAD,
            id=OUTPUT_NAME,
        )

        ui_file = self.generar_capa_ui(WATERMARK_TEXT, HOOK_TEXT)
        self.ensamblar_final(
            resized_filepath,
            ui_file,
            OUTPUT_NAME,
            DEBUG_VIDEO_FRAME,
        )
        if not DEBUG_VIDEO_FRAME:
            print("Saving config repo...")
            self.config_repo.add(c)

    def ensamblar_final(self, video_input, ui_png, video_output, debug=False):
        from rest_api.config import TEMP_DIR, OUTPUT_DIR # todo: improve
        salida_imagen = str(TEMP_DIR /  "debug_frame.png")
        salida_video = str(OUTPUT_DIR / f"{video_output}.mp4")
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
                salida_imagen,  # Salida como imagen
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
                salida_video,
            ]

        subprocess.run(ffmpeg_cmd, check=True)

    def generar_banner_from_html(self, texto, fuente_local):
        from html2image import Html2Image

        # 1. Transformar saltos de línea de Python a HTML
        # Esto permite que si tu hook_text tiene "\n", se renderice en varias líneas.
        texto_html = texto.replace("\n", "<br>")

        
        hti = Html2Image(size=(1200, 600), custom_flags=[
            '--no-sandbox', 
            '--disable-gpu', 
            '--hide-scrollbars',
            '--default-background-color=00000000'
        ])
        
        css = f"""
        @font-face {{
            font-family: 'MontserratLocal';
            src: url('file:///{fuente_local}');
        }}

        body {{ 
            background: transparent !important; 
            margin: 0; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            width: 100vw;
            overflow: hidden;
        }}

        .banner {{
            background: rgba(30, 30, 30, 0.85); 
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 2px solid rgba(255, 255, 255, 0.15);
            border-radius: 45px;
            padding: 50px 80px;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
            display: inline-block;
            max-width: 900px; /* Limitamos el ancho para forzar el balance de las 3 líneas */
        }}

        h1 {{
            color: white;
            font-family: 'MontserratLocal', sans-serif;
            font-size: 100px; /* Bajamos un poco el tamaño para acomodar 3 líneas mejor */
            font-weight: 900;
            margin: 0;
            letter-spacing: -2px;
            line-height: 1; /* Espaciado entre líneas profesional */
            text-shadow: 0 5px 15px rgba(0,0,0,0.4);
        }}
        """
        
        # Usamos la variable texto_html ya procesada
        html = f'<div class="banner"><h1>{texto_html}</h1></div>'

        output_name = 'banner_final.png'
        hti.screenshot(html_str=html, css_str=css, save_as=output_name)
        
        return output_name
                

    def generar_capa_ui(self, watermark_text, hook_text, output_png="temp/temp_ui.png"):
        from rest_api.config import TEMP_DIR, TEXT_FONT_PATH # todo: improve
        output_png = str(TEMP_DIR / "temp_ui.png")
        WATERMARK_TEXT_FONT_PATH = "C:/Windows/Fonts/CascadiaCode.ttf"
        CANVAS_SIZE = (1080, 1920)
        FUENTE_PATH = str(TEXT_FONT_PATH).replace("\\", "/")

        # Hook
        ruta_img = self.generar_banner_from_html(hook_text,FUENTE_PATH )
        hook = (ImageClip(ruta_img)
                    .with_position(("center", 1150))) # Mantén el margen de seguridad de la App
        # Watermark
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=55,
                color="gray",
                size=(460, 155),
                font=WATERMARK_TEXT_FONT_PATH,
            )
            .with_position((50, 15))
            .rotated(15)
        )

        # Logo
        from rest_api.config import ASSETS_DIR # todo: improve
        logo_path = str(ASSETS_DIR / "emoji_comment.png")
        logo = (
            ImageClip(logo_path)
            .resized(width=150)
            .with_position((800, 1035))
        )

        # Componemos y guardamos UN SOLO FRAME
        ui_composite = CompositeVideoClip(
            [hook, watermark, logo], size=CANVAS_SIZE, bg_color=None
        )
        ui_composite.save_frame(output_png, t=0)
        return output_png

        
    def get_segment(self, url, inicio, fin, force_download, id):
        from rest_api.config import TEMP_DIR # todo: improve
        temp_file = str(TEMP_DIR / f"{id}_segment_raw_download.mp4")
        file_doesnt_exist = not Path(temp_file).is_file()

        if file_doesnt_exist:
            self.download_segment_from_yt(inicio, fin, url, temp_file)
        elif force_download:
            file_to_remove = Path(temp_file)
            file_to_remove.unlink(missing_ok=True)  # delete file
            self.download_segment_from_yt(inicio, fin, url, temp_file)
        else:
            print(
                f"Raw file exists & force_download={force_download}, skipping raw download..."
            )

        resized_file = str(TEMP_DIR / f"{id}_segment_resized.mp4")
        resized_file_exists = Path(resized_file).is_file()

        if not resized_file_exists:
            # 2. Procesamiento local con GPU (Filtros corregidos + AMF)
            try:
                POS_Y = 180
                # Variables de control
                CANVAS_W, CANVAS_H = 1080, 1920
                FACTOR = 1.53  # Tu 1.5x vital
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



    def download_segment_from_yt(self, start_ts: str, end_ts: str, url: str, output_path: str):
        # Convertir "00:01:00" a segundos para la API nativa
        def to_seconds(ts):
            h, m, s = map(int, ts.split(":"))
            return h * 3600 + m * 60 + s

        start_sec = to_seconds(start_ts)
        end_sec = to_seconds(end_ts)

        ydl_opts = {
            "quiet": False,
            "no_warnings": True,
            "outtmpl": output_path,
            # CHANGE THIS: Remove the strict [ext=mp4] requirement.
            # We ask for best video + best audio and tell it to merge into mp4.
            "format": "bestvideo+bestaudio/best",
            "format_sort": ["res:4k", "ext:mp4:m4a"],
            "merge_output_format": "mp4",
            # Add this to handle the "tv downgraded" streams correctly
            "download_ranges": lambda info_dict, ydl: [
                {
                    "start_time": start_sec,
                    "end_time": end_sec,
                }
            ],
            "force_keyframes_at_cuts": True,
            #"sleep_interval": random.randint(5, 15),
            #"max_sleep_interval": 30,
            #"cookiefile": "youtube_cookies.txt",
            "extractor_args": {
                "youtube": {
                    # 'tv' or 'android' clients are great for avoiding bot-checks,
                    # but they require the broader format selection above.
                    "player_client": ["android"],
                    "player_skip": ["webpage", "configs"],
                }
            },
        }


        try:
            print(f"Starting download raw segment: {start_ts} - {end_ts}")

            start_time = time.perf_counter()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time:.4f} seconds")

            print("Raw segment downloaded successfuly")
        except Exception as e:
            print(f"Error while downloading: {e}")