# Multimodal Image Retrieval System

A production-style image search engine that lets users query a 31,000+ image dataset using **text** or **image** inputs, powered by OpenAI CLIP embeddings and a hybrid lexical + dense retrieval pipeline.

🔗 **Live Demo:** Deployed on [Hugging Face Spaces](https://jayanta2025-image-retrieval-system.static.hf.space/index.html) via Docker

📦 **Stack:** FastAPI · CLIP (ViT-B/32) · MongoDB Atlas Vector Search · BM25 · Docker

<img width="1919" height="973" alt="Screenshot 2026-07-22 164117" src="https://github.com/user-attachments/assets/e73c9a50-b86f-406a-970b-3d9ac00e2481" />

---

## Overview

This system indexes the Flickr30K dataset (31,000+ images) using CLIP embeddings and supports:

- **Text → Image search** — natural language queries return the most relevant images
- **Image → Image search** — upload an image to find visually similar ones
- **Hybrid search** — combines dense vector similarity using alpha-weighted for improved relevance

## Key Results
NOTE: It is CPU Inference, GPU will increase perfromance.

| Metric | Text Search | Image Search |
|---|---|---|
| Recall@1 | 92% | 98.5% |
| Recall@5 | 100% | 100% |
| MRR | 0.95 | 0.99 |
| p50 latency | 169ms | 2.5s |
| p95 latency | 386ms | 3.1s |
| p99 latency | 1.1s | 4.6s |

Benchmarked across **600 evaluation queries**, including distorted-image robustness testing to validate real-world resilience. Full methodology and results in [`benchmark.md`](./benchmark.md).

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────────┐
│   Client     │───▶│   FastAPI     │───▶│  CLIP Embedding     │
│ (HTML/JS UI) │     │   REST API   │     │  (text & image)     │
└──────────────┘     └──────────────┘     └──────────┬──────────┘
                                                     │
                                         ┌───────────▼────────────┐
                                         │  MongoDB Atlas Vector  │
                                         │  Search + BM25 Hybrid  │
                                         └────────────────────────┘
```

- **Embedding generation:** batch pipeline (GPU-optimized, fp16, resumable checkpointing) transforms and indexes vectors offline
- **Serving:** stateless FastAPI backend exposing REST endpoints for live search
- **Storage:** images hosted on Cloudinary; embeddings + metadata in MongoDB Atlas
- **Deployment:** containerized with Docker, running on Hugging Face Spaces (port 7860)

## Project Structure

```
├── api/                  # FastAPI application & routes
├── benchmark/            # Evaluation scripts & results
├── frontend/             # Frontend using HTML,CSS and JS
├── generate_embedding/   # CLIP embedding generation pipeline
├── hf_image_upload/      # Image hosting/upload utilities
├── Images/               # Sample/reference images
├── models/               # Model loading & inference logic
├── mongoDB/              # Vector search & DB integration
├── benchmark.md          # Full benchmark report (latency, recall, MRR)
├── Dockerfile            # Container build for HF Spaces deployment
├── dock-help-cmd         # Docker command reference
└── requirements.txt      # Python dependencies
```

## Tech Highlights

- Hybrid retrieval combining Text + Image CLIP embeddings, using alpha-weighted for tunable relevance
- Parallelized embedding pipeline (`ThreadPoolExecutor`) with GPU batch processing on Kaggle T4
- Rigorous benchmarking suite measuring latency percentiles (p50/p95/p99), Recall@k, and MRR across both search modalities
- Distortion robustness testing for image-to-image search reliability

## Running Locally

```bash
git clone <repo-url>
cd <repo-name>
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Or via Docker:

```bash
docker build -t image-retrieval .
docker run -p 7860:7860 image-retrieval
```

---

*Personal project, March 2026.*
