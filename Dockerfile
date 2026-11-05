# Hermetic Reproduction Container for MR-AST
# Google Gemma 4 Developer Agent Paper Track (Kaggle Competition ID: 163111)

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    patch \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command: run full test suite verifying all invariants
CMD ["pytest", "tests/", "-v"]

