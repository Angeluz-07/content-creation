FROM python:3.13-slim

WORKDIR /app

# extra deps: ffmpeg, node
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \ 
    libsm6 \
    libxext6 \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY deploy/download_worker/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY /src /app/src

CMD ["prefect", "flow", "serve", "src.workers.download:download", "--name", "main", "--limit", "2"]