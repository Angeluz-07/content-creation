from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

import whisper
import os
import glob
from pathlib import Path
from uuid import uuid5, NAMESPACE_DNS


def get_client(embedding_dimension, collection_name):
    # 2. Conexión a Qdrant
    client = QdrantClient(host="localhost", port=6333)
    vector_size = embedding_dimension

    # 3. Creación de la colección
    if not client.collection_exists(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Colección '{collection_name}' creada con dimensión {vector_size}")
    else:
        print(f"Collection '{collection_name}' exists with dimension {vector_size}")
    return client


class VideoSegmentRetriever:
    def __init__(self, client, collection_name, embedding_service):
        self.client = client
        self.collection_name = collection_name
        self.embedding_service = embedding_service

    def add_segment(self, id, text, metadata):
        vector: list[float] = self.embedding_service.get_vector(text)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{"id": id, "vector": vector, "payload": metadata}],
        )

    def search(self, text, top_k=5):
        """Busca segmentos similares a un texto dado."""        
        query_vector: list[float] = self.embedding_service.get_vector(text)
        results = self.client.query_points(
            collection_name=self.collection_name, query=query_vector, limit=top_k
        )
        return results


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


# -----
import webvtt


def vtt_time_to_seconds(timestamp):
    """Convierte formato VTT (HH:MM:SS.mmm) a segundos (float)."""
    parts = timestamp.split(":")
    # Maneja HH:MM:SS.mmm
    h, m = int(parts[0]), int(parts[1])
    s, ms = map(float, parts[2].split("."))
    return h * 3600 + m * 60 + s + (ms / 1000)


def find_candidates(vtt_path, retriever, threshold=0.75):
    vtt = webvtt.read(vtt_path)

    bloque_texto = ""
    start_ts_str = None
    candidatos = []

    for caption in vtt:
        if start_ts_str is None:
            start_ts_str = caption.start

        bloque_texto += caption.text + " "

        # Convertimos a segundos para la comparación
        start_sec = vtt_time_to_seconds(start_ts_str)
        end_sec = vtt_time_to_seconds(caption.end)

        if (end_sec - start_sec) >= 30:
            # 2. BÚSQUEDA
            resultados = retriever.search(bloque_texto, top_k=1)
            puntos = resultados.points if hasattr(resultados, "points") else resultados

            if puntos:
                mejor_resultado = puntos[0]
                # 3. Filtrar por confianza (Threshold)
                # NOTA: En versiones modernas, el score está en mejor_resultado.score
                if mejor_resultado.score >= threshold:
                    candidatos.append(
                        {
                            "source_start": start_ts_str,
                            "source_end": caption.end,
                            "match_file": mejor_resultado.payload.get("archivo", "N/A"),
                            "score": mejor_resultado.score,
                        }
                    )
            # Reset
            bloque_texto = ""
            start_ts_str = None

    return candidatos


import requests


class EmbeddingService:

    def __init__(self):
        self.url = "http://localhost:8001"

    def get_vector(self, text):
        response = requests.post(f"{self.url}/embed", json={"text": text})
        return response.json()["vector"]

    def get_dimension(self):
        response = requests.get(f"{self.url}/dimension")
        return response.json()["dimension"]


es = EmbeddingService()
collection_name = "video_segments"
client = get_client(es.get_dimension(), collection_name)
retriever = VideoSegmentRetriever(client, collection_name, es)

# feedb db, run once
# model_whisper = whisper.load_model("base")
# print("finished whisper load")
# video_folder = r"C:\Users\rmena\Desktop\dev\content-creation\segment_finder\.data\batch1_video_segments"
# feed_db(model_whisper, str(Path(video_folder)), retriever)

# checking retrieve
# result = retriever.search("el taka taka taka")

# import pdb; pdb.set_trace()

# find candidates
vtt_path = r"C:\Users\rmena\Desktop\dev\content-creation\discovery\test.es.vtt"
vtt_path = str(Path(vtt_path))
result = find_candidates(vtt_path, retriever)
import pdb; pdb.set_trace()

# todo: improve network overheard by sending all points either to embed or to db