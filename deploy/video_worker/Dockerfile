FROM python:3.13-slim

WORKDIR /app

# extra deps: ffmpeg(libsm6,libxext6), skia(libgl1,libegl1)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \ 
    libsm6 \
    libxext6 \
    libgl1 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

COPY deploy/video_worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

ENV MONGODB_URI=""
EXPOSE 8003

CMD ["prefect", "flow", "serve", "src.workers.video:video_build", "--name", "main", "--limit", "2"]