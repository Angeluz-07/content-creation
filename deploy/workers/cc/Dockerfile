FROM python:3.13-slim

WORKDIR /app

# extra deps: ffmpeg(libsm6,libxext6), skia(libgl1,libegl1), node
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \ 
    libsm6 \
    libxext6 \
    libgl1 \
    libegl1 \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY deploy/workers/cc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

CMD ["prefect", "worker", "start", "--pool", "local-docker-pool", "--limit", "4"]