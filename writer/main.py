import chromadb
import ollama

from text_generator_service import TextGenerator
from config import DEFAULT_MODEL
from domain.models import FewShotExample, Prompt
from typing import List

from dbs.md_repository import PostInRepository, PromptRepository

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

client = QdrantClient(host="localhost", port=6333)
collection_name = "posts_viejos"

test_emb = ollama.embeddings(model=DEFAULT_MODEL, prompt="test")["embedding"]
vector_size = len(test_emb) 

if not client.collection_exists(collection_name=collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

postin_repo = PostInRepository()

all_posts = postin_repo.get_all()
existing_ids = set()

if all_posts:
    postin_ids = [int(p.id) for p in all_posts]
    # Qdrant permite recuperar puntos específicos por ID
    existing_points = client.retrieve(
        collection_name=collection_name,
        ids=postin_ids,
        with_payload=False,
        with_vectors=False
    )
    existing_ids = {int(p.id) for p in existing_points}

points_to_upsert = []
for p in all_posts:
    if int(p.id) not in existing_ids:
        response = ollama.embeddings(model=DEFAULT_MODEL, prompt=p.seed)
        
        # En Qdrant guardamos el texto del post dentro del payload
        points_to_upsert.append(
            PointStruct(
                id=int(p.id),
                vector=response["embedding"],
                payload={
                    "seed_original": p.seed,
                    "content": p.content
                }
            )
        )

if points_to_upsert:
    client.upsert(
        collection_name=collection_name,
        points=points_to_upsert
    )

def obtener_ejemplos_rag(nueva_semilla, n_results=2) -> List[FewShotExample]:
    query_emb = ollama.embeddings(model=DEFAULT_MODEL, prompt=nueva_semilla)["embedding"]

    # REEMPLAZO: Usamos query_points en lugar de search
    response = client.query_points(
        collection_name=collection_name,
        query=query_emb,
        limit=n_results
    )

    ejemplos = []
    # Notar que recorremos 'response.points' que devuelve la API
    for hit in response.points:
        payload = hit.payload
        ejemplos.append(
            FewShotExample(
                id=str(hit.id),
                seed=payload["seed_original"],
                post=payload["content"]
            )
        )

    return ejemplos


# Traemos ejemplos dinámicos de la DB

prompt_repo = PromptRepository()
prompt: Prompt = prompt_repo.get_by_id("")

ejemplos_db = obtener_ejemplos_rag(prompt.user_content, n_results=2)
prompt.examples = ejemplos_db

generator = TextGenerator()
resultado = generator.generate(prompt)

print(f"Post Generado:\n{resultado.text}\n")
print(f"Duración: {resultado.creation_duration}s | Palabras: {resultado.num_words}")
