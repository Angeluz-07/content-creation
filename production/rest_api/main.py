import sys
from pathlib import Path

# This finds the 'backend' directory and adds it to the search path
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))
# INFO: the code above is to be able to run python rest_api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rest_api.routes import router

app = FastAPI()

# Handle CORS in local dev
origins= [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    
    allow_credentials=True,  # Allows cookies and authorization headers
    allow_methods=["*"],     # Allows all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],     # Allows all headers, including Authorization and Content-Type
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
