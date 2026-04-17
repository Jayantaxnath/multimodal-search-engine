# Multimodal Search Engine

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Multimodal image-text search using CLIP embeddings, FastAPI, MongoDB Atlas Search, and a lightweight frontend.

## Features

- Text-to-image search using caption text search and vector fallback.
- Image-to-image search using CLIP image embeddings.
- Hybrid image + text query support via weighted embedding fusion (`alpha`).
- Batch upload pipeline for embedding documents into MongoDB.

## Project Structure

- `backend/`: FastAPI app, model download script, Python dependencies.
- `frontened/`: HTML/CSS/JS UI for text and image queries.
- `pipelines/mongoDB/`: Notebook and checkpoint flow for bulk upload.
- `docs/`: Supporting docs, including MongoDB setup.
- `models/` and `backend/models/`: Local CLIP model cache.

## Requirements

- Python 3.10+
- MongoDB Atlas cluster (recommended for `$vectorSearch` and `$search`)
- Internet access (first model download only)

## Very Short Setup Pipeline

1. Clone repo.
2. Download dataset: [docs/data-setup.md](docs/data-setup.md).
3. Create MongoDB account + cluster: [docs/mongodb-setup.md](docs/mongodb-setup.md).
4. Get connection string and set `.env` (`MONGODB_DRIVER_STRING`).
5. Install requirements: `pip install -r backend/requirements.txt`.
6. Create embeddings file by running [pipelines/embedding_pipeline.ipynb](pipelines/embedding_pipeline.ipynb) (`dataset.pkl`).
7. Upload to MongoDB by running [pipelines/mongoDB/mongodb_upload.ipynb](pipelines/mongoDB/mongodb_upload.ipynb).
8. If paths changed, update notebook variables (`IMAGE_DIR`, `SAVE_PATH`, `DATA_PATH`) and [frontened/script.js](frontened/script.js) `IMAGE_BASE`.
9. Fix errors if any, then run backend: `cd backend && python app.py`.
10. Open [frontened/index.html](frontened/index.html) in browser.

Full quick flow: [docs/setup-pipeline-short.md](docs/setup-pipeline-short.md).

## Quick Start

1. Download and set up dataset:

- Follow [docs/data-setup.md](docs/data-setup.md).

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Configure environment variable in `.env` at project root:

```env
MONGODB_DRIVER_STRING=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority
```

4. Download CLIP model (first time only):

```bash
cd backend
python download_model.py
```

5. Upload embeddings to MongoDB:

- Open and run `pipelines/mongoDB/mongodb_upload.ipynb`, or
- Adapt the upload cells to run as a script.

6. Run backend API:

```bash
cd backend
python app.py
```

7. Open frontend:

- Open `frontened/index.html` in browser.

## API Endpoints

- `GET /`: health/home page
- `POST /search/text`: text query body

```json
{
  "query": "a dog running on grass",
  "top_k": 8
}
```

- `POST /search/image`: multipart image file, optional `query`, `alpha`, `top_k`

## MongoDB Notes

- Database name: `embeddings`
- Collection name: `embeddings_8k`
- Required Atlas indexes:
  - Search index on `captions.text` (name: `default`)
  - Vector index on `image_embedding` (name: `vector_index`)

Full setup steps are available in [docs/mongodb-setup.md](docs/mongodb-setup.md).
Data download/setup steps are available in [docs/data-setup.md](docs/data-setup.md).

## Troubleshooting

- `python-multipart` missing:
  - Install dependencies from `backend/requirements.txt` again.
- Model load fails with `local_files_only=True`:
  - Run `backend/download_model.py` first.
- Mongo connection fails:
  - Verify `MONGODB_DRIVER_STRING` and Atlas Network Access IP allowlist.
- Empty text search results:
  - Ensure the `default` Atlas Search index exists and is built.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
