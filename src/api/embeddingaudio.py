import io
from pathlib import Path
import numpy as np
import librosa
import onnxruntime as ort
from pydub import AudioSegment
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="Whisper-Base Audio Embedding API")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / ".data"
MODEL_PATH = DATA_DIR / "models" / "whisper_encoder.onnx"

print(f"🔍 Cargando Encoder Whisper-Base ONNX desde: {MODEL_PATH}")
try:
    session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
    print("✅ Modelo Whisper-Base cargado exitosamente.")
except Exception as e:
    print(f"⚠️ Alerta: Modelo no cargado en {MODEL_PATH}: {e}")
    session = None


def decode_m4a(audio_bytes: bytes, target_sr=16000) -> tuple[np.ndarray, float]:
    """Decodifica .m4a en RAM a una onda mono a 16kHz usando FFmpeg."""
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="m4a")
    duration = audio.duration_seconds

    if duration > 180:
        raise ValueError(f"El audio excede el límite de 3 minutos (Duración: {round(duration, 1)}s)")

    audio = audio.set_frame_rate(target_sr).set_channels(1)
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0
    return samples, duration


def get_mel_spectrogram_30s(samples: np.ndarray, target_sr=16000, target_frames=3000) -> np.ndarray:
    """
    Genera el espectrograma Mel de 80 canales y ajusta la dimensión 
    estrictamente a 3000 marcos (30s) aplicando padding con silencio.
    """
    mel = librosa.feature.melspectrogram(
        y=samples, sr=target_sr, n_mels=80, n_fft=400, hop_length=160
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    
    # Normalización del espectrograma [-1, 1]
    mel_norm = (mel_db + 40.0) / 40.0

    # Padding si es menor a 3000 marcos (30 segundos)
    current_frames = mel_norm.shape[1]
    if current_frames < target_frames:
        padding_needed = target_frames - current_frames
        padding = np.full((80, padding_needed), -1.0, dtype=np.float32)
        mel_norm = np.hstack([mel_norm, padding])
    elif current_frames > target_frames:
        mel_norm = mel_norm[:, :target_frames]

    return mel_norm


@app.post("/embed-audio")
async def embed_audio(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".m4a"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos .m4a")

    try:
        contents = await file.read()
        samples, duration = decode_m4a(contents)

        if session is None:
            raise HTTPException(status_code=500, detail="El modelo ONNX no está cargado")

        # 1. Calcular cuántos bloques de 30s (480,000 muestras a 16kHz) hay en el audio
        chunk_samples_len = 30 * 16000
        total_samples = len(samples)
        
        chunk_vectors = []

        # 2. Iterar por cada bloque de 30s sin perder ningún segundo de audio
        for start in range(0, total_samples, chunk_samples_len):
            chunk = samples[start:start + chunk_samples_len]
            mel_features = get_mel_spectrogram_30s(chunk)
            
            # Formato estricto para ONNX Whisper: [Batch=1, Mels=80, Time=3000]
            input_tensor = np.expand_dims(mel_features, axis=0).astype(np.float32)
            input_name = session.get_inputs()[0].name
            
            # Inferencia del bloque
            outputs = session.run(None, {input_name: input_tensor})
            
            # Pooling temporal del bloque
            hidden_states = outputs[0][0]
            chunk_vector = np.mean(hidden_states, axis=0)
            chunk_vectors.append(chunk_vector)

        # 3. PROMEDIO GLOBAL (Mean Pooling) + Normalización L2
        final_vector = np.mean(chunk_vectors, axis=0)
        norm = np.linalg.norm(final_vector)
        vector = (final_vector / (norm + 1e-8)).tolist()

        return {
            "filename": file.filename,
            "duration_seconds": round(duration, 2),
            "chunks_processed": len(chunk_vectors),
            "vector": vector
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando audio: {str(e)}")


@app.get("/dimension")
async def get_dimension():
    # Whisper Base utiliza 512 dimensiones en su Encoder
    return {"dimension": 512}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)