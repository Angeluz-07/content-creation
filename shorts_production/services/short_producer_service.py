from pathlib import Path
import sys

# Get grandparent and add to path
grandparent = Path(__file__).parent.parent.parent
sys.path.append(str(grandparent))
# INFO: the code above is to be able to import config.py from higher level folder

import random
import time
import subprocess
from pathlib import Path
from dbs.interfaces import IRepository
from moviepy import TextClip, CompositeVideoClip, ImageClip, ColorClip

from moviepy.video.tools.drawing import color_gradient
import numpy as np
from shorts_production.config import TEMP_DIR # todo: improve
from shorts_production.config import ASSETS_DIR # todo: improve
from shorts_production.config import TEXT_FONT_PATH
from shorts_production.config import OUTPUT_DIR # todo: improve

from domain.models import Config
from domain.services.yt_downloader import YTDownloader
from domain.services.video_builder import VideoBuilder
#todo move functions to domain service


class ShortProducer:
    def __init__(self, config_repo: IRepository, yt_downloader: YTDownloader = None, video_builder: VideoBuilder = None):
        self.config_repo = config_repo
        self.yt_downloader = yt_downloader or YTDownloader(output_path=str(TEMP_DIR))
        self.video_builder = video_builder or VideoBuilder(output_path=str(TEMP_DIR))

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

        file_id = OUTPUT_NAME
        raw_filepath = self.yt_downloader.get_video_segment(URL,START_SEGMENT,END_SEGMENT,FORCE_DOWNLOAD,file_id)
        
        resized_filepath = self.video_builder._resize_video_segment(raw_filepath, file_id)
        frame_filepath = self.video_builder._get_video_frame(raw_filepath)
        ui_file = self.generate_fixed_layer(WATERMARK_TEXT, HOOK_TEXT, frame_filepath)
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

    def generate_banner_from_html(self, text:str, font_path:str):        
        from html2image import Html2Image
        output_dir = str(TEMP_DIR)

        texto_html = text.replace("\n", "<br>")

        
        hti = Html2Image(size=(1200, 600), custom_flags=[
            '--no-sandbox', 
            '--disable-gpu', 
            '--hide-scrollbars',
            '--disable-direct-composition',
            '--log-level=3', 
            '--default-background-color=00000000'
        ], keep_temp_files=True, temp_path=output_dir)
        
        css = f"""
        @font-face {{
            font-family: 'MontserratLocal';
            src: url('file:///{font_path}');
        }}

        body {{
            background: transparent !important; 
            margin: 0; 
            padding: 0;
            display: block; 
            overflow: hidden;
        }}

        .banner {{
            background: black;
            display: block; 
            
            /* Dimensiones fijas obligatorias */
            width: 1100px; 
            height: 320px; 
            
            /* Centrado horizontal usando márgenes */
            margin: 0 auto; 
            
            /* Centrado interno del texto */
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
            box-sizing: border-box; /* Importante para que el padding no sume al tamaño */
            padding: 50px;
        }}

        h1 {{
            color: #E0E0E0;
            font-family: 'MontserratLocal', sans-serif;
            font-size: 100px; 
            font-weight: 900;
            margin: 0;
            line-height: 0.9;
            letter-spacing: 10px;
            text-shadow: 0px 1px 2px rgba(0,0,0,0.2)
        }}
        """
        
        # Usamos la variable texto_html ya procesada
        html = f'<div class="banner"><h1>{texto_html}</h1></div>'

        hti.output_path = output_dir
        output_name = 'banner_final.png'
        hti.screenshot(html_str=html, css_str=css, save_as=output_name)
        
        return output_name
                

    def generate_fixed_layer(self, watermark_text, hook_text, frame_filepath):
        output_png = str(TEMP_DIR / "temp_ui.png")
        WATERMARK_TEXT_FONT_PATH = "C:/Windows/Fonts/CascadiaCode.ttf"
        CANVAS_SIZE = (1080, 1920)
        TEXT_FONT_PATH_ = str(TEXT_FONT_PATH).replace("\\", "/")

        # Watermark
        watermark = (
            TextClip(
                text=watermark_text,
                font_size=55,
                color="white",
                size=(460, 155),
                font=TEXT_FONT_PATH_,
            )
            .with_opacity(0.5) 
            .with_position((0, 5))
            .rotated(15)
        )

        # Hook text
        banner_filename = self.generate_banner_from_html(hook_text, TEXT_FONT_PATH_)
        banner_filepath = str(TEMP_DIR / banner_filename)
        hook = (
            ImageClip(banner_filepath)
            .with_position(("center", 925))
        )

        # Logo
        logo_path = str(ASSETS_DIR / "emoji_comment.png")
        logo = (
            ImageClip(logo_path)
            .resized(width=150)
            .with_position((860, 860))
        )


        # Watermark
        frame = (
            ImageClip(frame_filepath)
            .resized(width=int(1080*1.9))
            .with_position(("center", 1220))
        )

        mask_array = color_gradient(
            frame.size, 
            p1=(0, 100), 
            p2=(0, 0),
            color_1=0, 
            color_2=1, 
            shape='linear'
        )
        mask_clip = ImageClip(mask_array, is_mask=True)
        frame_ = frame.with_mask(mask_clip)


        # Componemos y guardamos UN SOLO FRAME
        ui_composite = CompositeVideoClip(
            [watermark, frame, hook], size=CANVAS_SIZE, bg_color=None
        )
        ui_composite.save_frame(output_png, t=0)
        return output_png

    
