# MongoDB Atlas Setup Guide

This guide covers creating MongoDB Atlas, connecting your project, and preparing the required search/vector indexes.

## 1. Create Atlas Account and Cluster

1. Go to https://www.mongodb.com/atlas.
2. Create an account or sign in.
3. Create a project (for example: `multimodal-search`).
4. Create a cluster (M0 Free Tier is fine for testing).

## 2. Create Database User

1. Open Atlas: Security -> Database Access.
2. Click Add New Database User.
3. Choose username and strong password.
4. Privilege: Read and write to any database (or scoped to `embeddings`).
5. Save user.

## 3. Allow Network Access

1. Open Atlas: Security -> Network Access.
2. Add your current IP address, or use `0.0.0.0/0` for temporary testing.
3. Save.

## 4. Get Connection String

1. In Atlas, click Connect on your cluster.
2. Choose Drivers.
3. Copy the SRV string:

```text
mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority
```

## 5. Configure Environment Variable

Create or edit `.env` in the project root:

```env
MONGODB_DRIVER_STRING=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority
```

Your backend and notebook already read `MONGODB_DRIVER_STRING`.

## 6. Create Database and Collection

Your code uses:

- Database: `embeddings`
- Collection: `embeddings_8k`

These will be created automatically on first insert.

## 7. Upload Embeddings Data

Before this step, complete dataset download/setup in [docs/data-setup.md](data-setup.md).

1. Open `pipelines/mongoDB/mongodb_upload.ipynb`.
2. Run the connection/test cells.
3. Run the batch upload cell.
4. Confirm documents exist in `embeddings.embeddings_8k`.

## 8. Create Required Atlas Indexes

### A) Atlas Search index for text search

1. Atlas -> your cluster -> Search.
2. Create Search Index on collection `embeddings_8k`.
3. Index name: `default`.
4. Map field path `captions` for text search.

### B) Vector Search index for image embeddings

1. Atlas -> your cluster -> Search -> Create Index.
2. Choose Vector Search index.
3. Index name: `vector_index`.
4. Field path: `image_embedding`.
5. Dimensions: `512` (CLIP ViT-B/32 output size).
6. Similarity: `cosine`.

## 9. Validate from Backend

Run API:

```bash
cd backend
uvicorn app:app --reload
```

Test endpoints:

- `POST /search/text`
- `POST /search/image`

If text search returns no results while vector search works, re-check the `default` search index.

## 10. Common Fixes

- Authentication failed:
  - Verify username/password and special character escaping in URI.
- Timeout / cannot connect:
  - Check IP allowlist and internet access.
- `index not found` errors:
  - Confirm index names exactly match: `default`, `vector_index`.
- Vector query errors:
  - Ensure `image_embedding` values are numeric arrays of length 512.
