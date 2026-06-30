FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean

COPY deploy/embedding_api/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save_pretrained('/app/.data/model_weights') "
COPY /src /app/src

EXPOSE 8001

CMD ["uvicorn", "src.api.embedding:app", "--host", "0.0.0.0", "--port", "8001"]