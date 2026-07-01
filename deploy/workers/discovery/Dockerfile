FROM python:3.13-slim

WORKDIR /app

# extra deps: ffmpeg(libsm6,libxext6)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \ 
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY deploy/workers/discovery/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY /src /app/src

CMD ["prefect", "flow", "serve", "src.workers.discovery:discovery", "--name", "main", "--limit", "2"]