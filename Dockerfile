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
        cmake \
        git \
        git-lfs \
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
    && git lfs install \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Python build tools (Crucial for 3.13 source compilation)
RUN python -m pip install --upgrade pip setuptools wheel Cython
# Install Python requirements from subfolder
COPY aiml-unified-service/requirements.txt requirements.txt

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application source code
COPY aiml-unified-service/ .
# 5. Pull real binary weights if git LFS pointers exist
RUN if [ -d ".git" ]; then git lfs pull; fi

# 6. Pre-create output directory for charts
RUN mkdir -p modules/skill_demand/outputs outputs

EXPOSE ${PORT}

# Run FastAPI app with dynamic Render $PORT binding (falls back to 10000 locally)
CMD ["sh", "-c", "exec python -u -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --log-level debug"]