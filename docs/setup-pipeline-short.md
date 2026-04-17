# Short Setup Pipeline (Clone to Run)

Use this quick order to run the project end-to-end.

## 1. Clone

```bash
git clone <your-repo-url>
cd multimodel-search-engine
```

## 2. Download Data

- Follow [data setup](data-setup.md).

## 3. Create MongoDB Atlas Account

- Follow [MongoDB setup](mongodb-setup.md#1-create-atlas-account-and-cluster).

## 4. Get MongoDB Driver String

- Follow [get connection string](mongodb-setup.md#4-get-connection-string).
- Put it in `.env`:

```env
MONGODB_DRIVER_STRING=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority
```

## 5. Install Requirements

```bash
pip install -r backend/requirements.txt
```

## 6. Create `dataset.pkl` (Embeddings)

- Run notebook: [pipelines/embedding_pipeline.ipynb](../pipelines/embedding_pipeline.ipynb)
- Output: `dataset.pkl` (embedding records before MongoDB upload)

## 7. Upload `dataset.pkl` to MongoDB

- Run notebook: [pipelines/mongoDB/mongodb_upload.ipynb](../pipelines/mongoDB/mongodb_upload.ipynb)

## 8. Path Check (Important if folders changed)

If you moved folders, update these paths:

1. In [pipelines/embedding_pipeline.ipynb](../pipelines/embedding_pipeline.ipynb):
- `IMAGE_DIR`
- captions file path (for `captions.txt`)
- `SAVE_PATH` for `dataset.pkl`

2. In [pipelines/mongoDB/mongodb_upload.ipynb](../pipelines/mongoDB/mongodb_upload.ipynb):
- `DATA_PATH` (path to `dataset.pkl`)

3. In [frontened/script.js](../frontened/script.js):
- `IMAGE_BASE` (path to image directory)

## 9. Fix Errors if Any

- Re-run failed cell or API startup command after fixing paths/env.
- Common fixes are listed in [README troubleshooting](../README.md#troubleshooting).

## 10. Run Backend and Open UI

Run backend (FastAPI app):

```bash
cd backend
python app.py
```

Open UI:

- [frontened/index.html](../frontened/index.html)
