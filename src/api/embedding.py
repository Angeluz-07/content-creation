from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path
import os
from sentence_transformers import SentenceTransformer

DATA_DIR = Path(__file__).parent.parent.parent / ".data"
MODEL_DIR = str(DATA_DIR / "model_weights")
MODEL_NAME = "all-MiniLM-L6-v2"

if os.path.exists(os.path.join(MODEL_DIR, "config.json")):
    print("🚀 Weights loaded from volume...")    
    model = SentenceTransformer(MODEL_DIR)
    #model.save_pretrained(MODEL_DIR)
else:
    print("⚠️ Didnt find weights, downloading...")

    model = SentenceTransformer(MODEL_NAME)
    # model = SentenceTransformer(
    #     MODEL_DIR, backend="onnx", model_kwargs={"file_name": "model.onnx"}
    # )


app = FastAPI()


class TextRequest(BaseModel):
    text: str


class TextBatchRequest(BaseModel):
    texts: List[str]


@app.post("/embed")
def get_embedding(request: TextRequest):
    try:
        # 2. Generamos el flat array (vector)
        # .encode() devuelve un numpy array, .tolist() lo hace serializable a JSON
        vector = model.encode(request.text).tolist()
        return {"vector": vector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embed_batch")
def get_embeddings(request: TextBatchRequest):
    # Esto es una operación optimizada por el modelo
    return {"vectors": model.encode(request.texts).tolist()}


@app.get("/dimension")
async def get_dimension():
    # 3. Retornamos la dimensión fija (útil para inicializar Qdrant)
    return {"dimension": model.get_embedding_dimension()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
