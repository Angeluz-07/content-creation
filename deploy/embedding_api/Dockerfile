FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean

COPY deploy/embedding_api/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY /src /app/src

EXPOSE 8001

CMD ["uvicorn", "src.entrypoints.embedding_api:app", "--host", "0.0.0.0", "--port", "8001"]