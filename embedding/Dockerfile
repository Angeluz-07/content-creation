FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001 

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]