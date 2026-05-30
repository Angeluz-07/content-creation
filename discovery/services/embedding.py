import requests


class EmbeddingService:

    def __init__(self):
        self.url = "http://localhost:8001"

    def get_vector(self, text):
        # better use batch to process list of texts to avoid network overhead
        response = requests.post(f"{self.url}/embed", json={"text": text})
        return response.json()["vector"]

    def get_vectors(self, texts: list[str]):
        response = requests.post(f"{self.url}/embed_batch", json={"texts": texts})
        return response.json()["vectors"]

    def get_dimension(self):
        response = requests.get(f"{self.url}/dimension")
        return response.json()["dimension"]