FROM python:3.13-slim

WORKDIR /app

# extra deps: ffmpeg, node
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY deploy/production_api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /app/src

ENV MONGODB_URI=""
ENV REDIS_URI=""
EXPOSE 8000

CMD ["uvicorn", "src.entrypoints.production_api.main:app", "--host", "0.0.0.0", "--port", "8000"]