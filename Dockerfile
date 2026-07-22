FROM python:3.11-slim

WORKDIR /code

# Layer 1: system deps (rarely changes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: python deps (only rebuilds if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Layer 3: app code (changes often, cheap to rebuild) ---
COPY . .

EXPOSE 8000
ENV PORT=8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# EXPOSE 7860
# ENV PORT=7860
# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]