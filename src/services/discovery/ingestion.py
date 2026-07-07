import os
import glob
from pathlib import Path
from uuid import uuid5, NAMESPACE_DNS

from src.dbs.qdrant import IVectorStore #todo:improve


class Ingester:
    def __init__(self, vector_store: IVectorStore, embedder, transcriber, ingestion_dir):
        self.vector_store = vector_store
        self.embedder = embedder
        self.transcriber = transcriber
        self.ingestion_dir = ingestion_dir

    def run(self, data):
        print("Reached ingester ", data.get("folder_name"))
        target_dir =  str(Path(self.ingestion_dir) / data.get("folder_name") )
        print("Path to process ", target_dir)
        result = self.generate_transcriptions(target_dir)
        self.save_transcriptions(result)
        print(f"Successfully proccessed {len(result)} items")

    def save_transcriptions(self, transcriptions):
        texts = [t["metadata"]["text"] for t in transcriptions]
        vectors = self.embedder.get_vectors(texts)
        for i, t in enumerate(transcriptions):
            id = t["id"]
            vector = vectors[i]
            metadata = t["metadata"]
            self.vector_store.add(id, vector, metadata)

    def transcribe_video(self, video_path: str) -> dict:
        """
        Transcribe el video completo optimizando la calidad.
        Devuelve el texto completo y los segmentos nativos.
        """
        print(f"Procesando archivo: {os.path.basename(video_path)}...")

        # Transcripción nativa
        transcription = self.transcriber.transcribe(video_path)

        return {
            "filename": os.path.basename(video_path),
            "text": transcription["text"],
            "segments": transcription["segments"],
        }

    def generate_transcriptions(self, directorio_videos: str) -> list:
        """
        Procesa el directorio y devuelve la transcripción limpia y completa por video.
        """
        video_files = glob.glob(os.path.join(directorio_videos, "*.mp4"))
        result = []

        for video_path in video_files[:1]:
            data = self.transcribe_video(video_path)

            # Generar un ID único para el video completo
            unique_string = f"{data['filename']}_completo"
            video_id = str(uuid5(NAMESPACE_DNS, unique_string))

            result.append(
                {
                    "id": video_id,
                    "metadata": {
                        "text": data["text"],
                        "filename": data["filename"],
                        "duration": (
                            round(data["segments"][-1]["end"], 2)
                            if data["segments"]
                            else 0
                        ),
                        "transcriber": self.transcriber.name,
                    },
                }
            )

        return result

    @staticmethod
    def chunk_transcription(
        transcription_data: dict, target_duration: float = 30.0
    ) -> list:
        """
        Función extra/utilitaria para cuando necesites chopear la transcripción
        en bloques de tiempo específicos (ej. para embeddings/RAG).
        """
        chunks = []
        bloque_texto = ""
        start_ts = None
        archivo = transcription_data["archivo"]

        for segment in transcription_data["segments"]:
            if start_ts is None:
                start_ts = segment["start"]

            bloque_texto += segment["text"] + " "

            if segment["end"] - start_ts >= target_duration:
                metadata = {
                    "texto": bloque_texto.strip(),
                    "archivo": archivo,
                    "ts_start": round(start_ts, 2),
                    "ts_end": round(segment["end"], 2),
                }
                unique_string = f"{archivo}_{metadata['ts_start']}"
                chunk_id = str(uuid5(NAMESPACE_DNS, unique_string))

                chunks.append(
                    {"id": chunk_id, "text": bloque_texto.strip(), "metadata": metadata}
                )

                # Reset
                bloque_texto = ""
                start_ts = None

        # Residuo final
        if bloque_texto and transcription_data["segments"]:
            metadata = {
                "texto": bloque_texto.strip(),
                "archivo": archivo,
                "ts_start": round(start_ts if start_ts is not None else 0, 2),
                "ts_end": round(transcription_data["segments"][-1]["end"], 2),
            }
            unique_string = f"{archivo}_{metadata['ts_start']}"
            chunk_id = str(uuid5(NAMESPACE_DNS, unique_string))
            chunks.append(
                {"id": chunk_id, "text": bloque_texto.strip(), "metadata": metadata}
            )

        return chunks
