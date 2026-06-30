# API + ingestion image (no torch/transformers — those live in the [ml] extra,
# run as an offline job to generate embeddings).
FROM python:3.11-slim

WORKDIR /app

# Copy sources first so setuptools can find the packages during install.
COPY pyproject.toml ./
COPY app ./app
COPY pipeline ./pipeline
COPY api ./api

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
