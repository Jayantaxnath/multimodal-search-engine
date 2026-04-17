import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

import io
import os
import math
from dotenv import load_dotenv

from pymongo import MongoClient
from pydantic import BaseModel

load_dotenv()
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# MonggoDB Config
MONGO_URI = os.getenv("MONGODB_DRIVER_STRING")
DB_NAME = "embeddings"
COLLECTION = "embeddings_8k"

# Init FastAPI App
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models Globally (CLIP)
MODEL_PATH = "./models"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", cache_dir=MODEL_PATH, local_files_only=True)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", cache_dir=MODEL_PATH, local_files_only=True)

print("models loaded")
# MongoDB collection
client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION]

# Request Schema
class TextQuery(BaseModel):
    query: str
    top_k: int = 8  # default val


# Embedding Functions (text/image)
def get_text_embedding(text_query: str):

    inputs = processor(
        text=text_query, return_tensors="pt", padding=True, truncation=True
    )

    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    # normalize
    text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
    embedding = text_features[0].tolist()

    return embedding


def get_image_embedding(image_bytes: bytes):

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        features = model.get_image_features(**inputs)
    features = features / features.norm(p=2, dim=1, keepdim=True)

    embedding = features.squeeze().tolist()
    return embedding


def combine_embeddings(image_emb, text_emb, alpha: float):
    # final_embedding = alpha * image_emb + (1-alpha) * text_emb
    combined = [alpha * i + (1.0 - alpha) * t for i, t in zip(image_emb, text_emb)]
    norm = math.sqrt(sum(v * v for v in combined))
    if norm == 0:
        return combined
    return [v / norm for v in combined]

# MongoDB Text Search
def text_search(query_text, limit=8):
    pipeline = [
        {
            "$search": {
                "index": "default",
                "text": {
                    "query": query_text,
                    "path": "captions"   # ✅ updated
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "image_url": 1,
                "captions": 1,
                "score": {"$meta": "searchScore"}
            }
        },
        {
            "$limit": limit
        }
    ]
    
    return list(collection.aggregate(pipeline))

# MongoDB Vector Search
def vector_search(query_embedding, top_k=10, page=1):
    skip = (page - 1) * top_k

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "image_embedding",
                "queryVector": query_embedding,
                "numCandidates": 200,
                "limit": top_k + skip,  # fetch extra
            }
        },
        {"$skip": skip},  # pagination
        {"$limit": top_k},
        {
            "$project": {
                "_id": 0,
                "image_url": 1,
                "captions": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    return list(collection.aggregate(pipeline))


# Routes
@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Multimodal Image Search</title>
    </head>
    <body>
        <h1>Endpoints activated.</h1>
    </body>
    </html>
    """
    return html_content

@app.post("/search/text")
def search_text(data: TextQuery):
    results = text_search(data.query, data.top_k)

    # Fallback to semantic vector search when Atlas text search has no hits.
    if not results:
        emb = get_text_embedding(data.query)
        results = vector_search(emb, data.top_k)

    return {"results": results, "count": len(results)}


@app.post("/search/image")
async def search_image(
    file: UploadFile = File(...),
    top_k: int = 8,
    query: str | None = None,
    alpha: float = 0.7,
):
    image_bytes = await file.read()
    image_emb = get_image_embedding(image_bytes)

    emb = image_emb
    if query and query.strip():
        alpha = max(0.0, min(1.0, alpha))
        text_emb = get_text_embedding(query.strip())
        emb = combine_embeddings(image_emb, text_emb, alpha)

    results = vector_search(emb, top_k)
    return {"results": results}


# run: uvicorn app:app --reload

if __name__ == "__main__":
    print("For UI docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)