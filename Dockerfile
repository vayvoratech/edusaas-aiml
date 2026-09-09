FROM python:3.13-bookworm

ENV OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    VECLIB_MAXIMUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000


WORKDIR /app

# OpenCV / MediaPipe runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        curl \
        nodejs \
        npm \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
        libegl1 \
        libgles2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements from subfolder
COPY aiml-unified-service/requirements.txt requirements.txt

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application source code
COPY aiml-unified-service/ .

EXPOSE ${PORT}

# Run FastAPI app with dynamic Render $PORT binding (falls back to 10000 locally)
CMD ["sh", "-c", "exec python -u -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --log-level debug"]