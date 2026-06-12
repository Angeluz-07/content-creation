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

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MONGODB_URI=""
EXPOSE 8003

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8003"]