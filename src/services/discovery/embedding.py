import requests
import time

class Embedder:

    def __init__(self, embedder_uri):
        self.url = embedder_uri

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

    def wait_until_ready(self, timeout_seconds=30, interval=2):
        """
        Bloquea la ejecución y espera a que la API de embeddings esté 100% lista.
        Útil para esperar a que el modelo termine de cargarse en memoria.
        """
        start_time = time.time()
        print(f"Waiting for embedder service en {self.url}...")
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Intentamos llamar al endpoint más ligero para verificar la salud del servicio
                response = requests.get(f"{self.url}/dimension", timeout=3)
                if response.status_code == 200:
                    print("✅ Embedding service ready")
                    return True
            except requests.RequestException:
                # Si da error de conexión o timeout, ignoramos y seguimos esperando
                pass
            
            time.sleep(interval)
            
        # Si se agota el tiempo, lanzamos un error claro
        raise TimeoutError(
            f"❌ El servicio de embeddings no estuvo listo tras {timeout_seconds} segundos."
        )