FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# OpenCV / MediaPipe runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements from subfolder
COPY aiml-unified-service/requirements.txt requirements.txt

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application source code
COPY aiml-unified-service/ .

EXPOSE ${PORT}

# Run FastAPI app with dynamic Render $PORT binding (falls back to 8000 locally)
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]