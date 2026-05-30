from discovery.dbs.interfaces import IVectorRetriever


class Something:
    def __init__(self, retriever: IVectorRetriever, embedder):
        self.retriever = retriever
        self.embedder = embedder

    def search(self, text, top_k=5):
        """Busca segmentos similares a un texto dado."""
        vector = self.embedder.get_vector(text)
        results = self.retriever.search_by_vector(vector, top_k)
        return results

    def add(self, id, text, metadata):
        vector = self.embedder.get_vector(text)
        self.retriever.add_vector(id, vector, metadata)
