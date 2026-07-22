import io
import os
import torch
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from pymongo import MongoClient
from dotenv import load_dotenv

# Config & Initialization
load_dotenv()
MODEL_PATH = "./models"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI(title="Multimodal Search API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Load Models
model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32", cache_dir=MODEL_PATH
).to(DEVICE)
processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32", cache_dir=MODEL_PATH
)
model.eval()


# Database: MongoDB
load_dotenv()
MONGODB_DRIVER_URI = os.getenv("MONGODB_DRIVER_STRING")
if not MONGODB_DRIVER_URI:
    raise RuntimeError("MONGODB_DRIVER_STRING env var not set (set it in HF Space secrets)")

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_DRIVER_URI, serverSelectionTimeoutMS=5000)
    collection = client["database_embd"]["embeddings_31k"]
    client.admin.command("ping")
    print("[CONNECTED] MongoDB connection successful.")
except Exception as e:
    print("[ERROR] MongoDB connection failed:", e)


# Schemas
class TextQuery(BaseModel):
    query: str
    top_k: int = 10


# --- Embedding & Logic Functions ---

def get_text_embedding(text: str):
    inputs = processor(
        text=text, return_tensors="pt", padding=True, truncation=True
    ).to(DEVICE)
    with torch.no_grad():
        features = model.get_text_features(**inputs)
    return features / features.norm(p=2, dim=-1, keepdim=True)


def get_image_embedding(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    return features / features.norm(p=2, dim=1, keepdim=True)


def combine_embeddings(img_emb, txt_emb, alpha: float):
    alpha = max(0.0, min(1.0, alpha))
    combined = alpha * img_emb + (1.0 - alpha) * txt_emb
    return combined / combined.norm(p=2, dim=-1, keepdim=True)


# --- Routes ---
@app.get("/")
def home():
    return {"message": "FastAPI is running."}


@app.post("/search/text")
def search_text(data: TextQuery):
    pipeline = [
        {
            "$search": {
                "index": "default",
                "text": {"query": data.query, "path": "captions"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "image_url": 1,
                "captions": 1,
                "score": {"$meta": "searchScore"},
            }
        },
        {"$limit": data.top_k},
    ]
    results = list(collection.aggregate(pipeline))

    if not results:
        emb = get_text_embedding(data.query).squeeze().tolist()
        pipeline_vec = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "image_embedding",
                    "queryVector": emb,
                    "numCandidates": 100,
                    "limit": data.top_k,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "image_url": 1,
                    "captions": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
        results = list(collection.aggregate(pipeline_vec))

    return {"results": results, "count": len(results)}


@app.post("/search/image")
async def search_image(file: UploadFile = File(...), top_k: int = 10, query: str = None, alpha: float = 0.7):
    try:
        image_bytes = await file.read()
        img_emb = get_image_embedding(image_bytes)

        final_emb = img_emb
        if query and query.strip():
            txt_emb = get_text_embedding(query.strip())
            final_emb = combine_embeddings(img_emb, txt_emb, alpha)

        query_vector = final_emb.squeeze().tolist()

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "image_embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": top_k,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "image_url": 1,
                    "captions": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
        
        results = list(collection.aggregate(pipeline))
        
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # port = int(os.getenv("PORT", 7860))
    # uvicorn.run(app, host="0.0.0.0", port=port)
    uvicorn.run(app, host="localhost", port=8000)