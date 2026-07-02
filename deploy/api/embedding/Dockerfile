FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean

COPY deploy/api/embedding/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir='/app/.data/fastembed_cache')"
COPY /src /app/src

EXPOSE 8002

CMD ["uvicorn", "src.api.embedding_fastembed:app", "--host", "0.0.0.0", "--port", "8002"]