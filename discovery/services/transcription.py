from abc import ABC, abstractmethod
import os
from pathlib import Path
import os
import time
import subprocess
import tempfile
from pathlib import Path
from groq import Groq


class ITranscriber(ABC):
    @abstractmethod
    def transcribe(self, video_path: str) -> str:
        pass


class GroqAudioTranscriber(ITranscriber):
    def __init__(self, api_key: str):
        # API Key desde las variables de entorno de Windows
        self.client = Groq(api_key=api_key)
        print("Iniciando Groq transcriber...")
        self.name = "groq"
        self.model = "whisper-large-v3-turbo"

        # El Transcriber ahora es el dueño y protector de su propio ritmo
        self.SAFE_PAUSE = 20.0

    def _extract_audio_native(self, video_path: str) -> str:
        """
        Extrae la pista de audio a un contenedor .m4a (AAC)
        usando FFmpeg nativo de forma silenciosa.
        """
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".m4a")
        temp_audio.close()

        # fmt: off
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",  # Deshabilitar flujo de video
            "-c:a", "aac",  # Códec AAC nativo para .m4a
            "-ac", "1",  # Convertir a Mono (óptimo para IA)
            "-ar", "16000",  # Frecuencia nativa de Whisper (16Khz)
            "-b:a", "64k",  # Bitrate ligero pero nítido para voces
            temp_audio.name,
        ]
        # fmt: on

        subprocess.run(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return temp_audio.name

    def transcribe(self, file_path: str) -> dict:
        """
        Acepta videos (.mp4) o audios directos (.m4a).
        Aplica la pausa de seguridad interna antes de retornar.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

        is_video = path.suffix.lower() in [".mp4", ".mkv", ".mov", ".avi"]
        active_audio_path = (
            self._extract_audio_native(file_path) if is_video else file_path
        )

        print(f"[{path.name}] Enviando audio a Groq Cloud...")

        try:
            with open(active_audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.model,
                    language="es",
                    temperature=0.0,
                    response_format="verbose_json",
                )

            segments_list = []
            if hasattr(transcription, "segments"):
                for segment in transcription.segments:
                    segments_list.append(
                        {
                            "start": segment.get("start"),
                            "end": segment.get("end"),
                            "text": segment.get("text", "").strip(),
                        }
                    )

            # El Transcriber duerme el hilo aquí para proteger la API Key
            print(f"⏱️ Respetando cuotas de Groq. Esperando {self.SAFE_PAUSE}s...")
            time.sleep(self.SAFE_PAUSE)

            return {"text": transcription.text.strip(), "segments": segments_list}

        finally:
            if is_video and os.path.exists(active_audio_path):
                os.remove(active_audio_path)
