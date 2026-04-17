# Data Download and Setup Guide

This project expects the Flickr8k dataset and local folder names to match the frontend and pipeline paths.

## 1. Download Flickr8k

Use one of these sources:

- Kaggle: https://www.kaggle.com/datasets/adityajn105/flickr8k
- Any trusted mirror that provides:
  - `Images/` folder
  - `captions.txt`

## 2. Create Required Folder Structure

From project root, ensure this structure exists:

```text
data/
  Flickr8k dataset/
    Images/
    captions.txt
```

Important: Keep the folder name exactly `Flickr8k dataset` (including the space), because your frontend uses this path.

## 3. Place Files

- Put all image files into:
  - `data/Flickr8k dataset/Images/`
- Put captions file into:
  - `data/Flickr8k dataset/captions.txt`

## 4. Verify Paths Used by Project

- Frontend image base path:
  - `frontened/script.js` -> `../data/Flickr8k dataset/Images/`
- Upload notebook uses embeddings pickle:
  - `pipelines/mongoDB/mongodb_upload.ipynb` -> `../../data/dataset.pkl` (current default)

## 5. Build Embeddings Dataset (if missing)

If `dataset.pkl` does not exist, run your embedding pipeline notebook first and set `SAVE_PATH` to `../../data/dataset.pkl`:

- `pipelines/embedding_pipeline.ipynb`

Then run MongoDB upload notebook:

- `pipelines/mongoDB/mongodb_upload.ipynb`

## 6. Quick Validation

1. Open `frontened/index.html`.
2. Run backend API (`cd backend && python app.py`).
3. Run a text query.
4. Confirm result images are displayed.

If images do not load, re-check folder names and image path in `frontened/script.js`.
