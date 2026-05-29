from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

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


# ---


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

    def search_by_vector(self, query_vector, top_k=5):
        """Busca segmentos similares a un texto dado."""
        results = self.client.query_points(
            collection_name=self.collection_name, query=query_vector, limit=top_k
        )
        return results


# -----
import webvtt


def vtt_time_to_seconds(timestamp):
    """Convierte formato VTT (HH:MM:SS.mmm) a segundos (float)."""
    parts = timestamp.split(":")
    # Maneja HH:MM:SS.mmm
    h, m = int(parts[0]), int(parts[1])
    s, ms = map(float, parts[2].split("."))
    return h * 3600 + m * 60 + s + (ms / 1000)


import requests


class EmbeddingService:

    def __init__(self):
        self.url = "http://localhost:8001"

    def get_vector(self, text):
        # better use batch to process list of texts to avoid network overhead
        response = requests.post(f"{self.url}/embed", json={"text": text})
        return response.json()["vector"]

    def get_vectors(self, texts: list[str]):
        response = requests.post(f"{self.url}/embed_batch", json={"texts": texts})
        return response.json()["vectors"]

    def get_dimension(self):
        response = requests.get(f"{self.url}/dimension")
        return response.json()["dimension"]


def extraer_bloques(vtt_path):
    vtt = webvtt.read(vtt_path)
    bloques = []
    texto_actual = ""
    start_ts = None

    for caption in vtt:
        if start_ts is None:
            start_ts = caption.start
        texto_actual += caption.text + " "

        if (vtt_time_to_seconds(caption.end) - vtt_time_to_seconds(start_ts)) >= 30:
            bloques.append(
                {"texto": texto_actual.strip(), "start": start_ts, "end": caption.end}
            )
            texto_actual = ""
            start_ts = None
    return bloques


def find_candidates(vtt_path, retriever, threshold=0.77):
    # 1. Extraer (Solo CPU)
    bloques = extraer_bloques(vtt_path)
    textos = [b["texto"] for b in bloques]
    # 2. Inferencia Batch (Un solo round-trip de red)
    vectores = retriever.embedding_service.get_vectors(textos)

    # 3. Procesamiento final
    candidatos = []
    for i, bloque in enumerate(bloques):
        # Aquí puedes usar retriever.search_by_vector si tu retriever lo permite
        # para evitar volver a calcular el embedding
        resultados = retriever.search_by_vector(vectores[i], top_k=1)
        points = resultados.points if hasattr(resultados, "points") else resultados
        mejor_resultado = points[0]
        if mejor_resultado.score >= threshold:
            candidatos.append(
                {
                    "start": bloque["start"],
                    "end": bloque["end"],
                    "score": mejor_resultado.score,
                    "match": mejor_resultado.payload.get("archivo"),
                    "texto": bloque["texto"]
                }
            )
    return candidatos


es = EmbeddingService()
collection_name = "video_segments"
client = get_client(es.get_dimension(), collection_name)
retriever = VideoSegmentRetriever(client, collection_name, es)

# feedb db, run once
# model_whisper = whisper.load_model("base")
# print("finished whisper load")
# video_folder = r"C:\Users\rmena\Desktop\dev\content-creation\segment_finder\.data\batch1_video_segments"
# feed_db(model_whisper, str(Path(video_folder)), retriever)

# find candidates
vtt_path = r"C:\Users\rmena\Desktop\dev\content-creation\discovery\test2.es.vtt"
vtt_path = str(Path(vtt_path))
result = find_candidates(vtt_path, retriever)
from pprint import pprint
pprint(result)
import pdb; pdb.set_trace()
# todo: improve network overheard by sending all points either to embed or to db
