FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Descargar Whisper-Base Encoder ONNX (~75MB)
RUN mkdir -p /app/.data/models && \
    curl -L -o /app/.data/models/whisper_encoder.onnx \
    https://huggingface.co/onnx-community/whisper-base/resolve/main/onnx/encoder_model.onnx


COPY deploy/api/embeddingaudio/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY /src /app/src

EXPOSE 8002

CMD ["uvicorn", "src.api.embeddingaudio:app", "--host", "0.0.0.0", "--port", "8002"]