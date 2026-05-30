import os
import glob
from pathlib import Path
from uuid import uuid5, NAMESPACE_DNS


# -------
def feed_db(model_whisper, directorio_videos, retriever):
    video_files = glob.glob(os.path.join(directorio_videos, "*.mp4"))

    for video_path in video_files:
        print(f"Procesando archivo: {os.path.basename(video_path)}...")

        # Whisper procesa y devuelve segmentos con timestamps
        result = model_whisper.transcribe(video_path, fp16=False)

        # Lógica para agrupar segmentos en bloques de ~30s
        bloque_texto = ""
        start_ts = 0

        for segment in result["segments"]:
            # Si el bloque es muy corto, seguimos acumulando
            if not bloque_texto:
                start_ts = segment["start"]

            bloque_texto += segment["text"] + " "

            # Si superamos los 30s, guardamos y reseteamos
            if segment["end"] - start_ts >= 30:
                metadata = {
                    "texto": bloque_texto.strip(),
                    "archivo": os.path.basename(video_path),
                    "ts_start": round(start_ts, 2),
                    "ts_end": round(segment["end"], 2),
                }
                unique_string = f"{metadata['archivo']}_{metadata['ts_start']}"
                id = str(uuid5(NAMESPACE_DNS, unique_string))
                # Aquí usamos tu función de retriever
                retriever.add_segment(id, bloque_texto.strip(), metadata)

                # Reset para el siguiente bloque
                bloque_texto = ""

        # Guardar el último residuo si quedó algo
        if bloque_texto:
            metadata = {
                "texto": bloque_texto.strip(),
                "archivo": os.path.basename(video_path),
                "ts_start": start_ts,
                "ts_end": result["segments"][-1]["end"],
            }
            unique_string = f"{metadata['archivo']}_{metadata['ts_start']}"
            id = str(uuid5(NAMESPACE_DNS, unique_string))
            retriever.add_segment(id, bloque_texto.strip(), metadata)

    print("Indexación finalizada.")


# feedb db, run once
# model_whisper = whisper.load_model("base")
# print("finished whisper load")
# video_folder = r"C:\Users\rmena\Desktop\dev\content-creation\segment_finder\.data\batch1_video_segments"
# feed_db(model_whisper, str(Path(video_folder)), retriever)
