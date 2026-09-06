FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

# Install OpenJDK 21, GCC, G++, build tools, and OpenCV/MediaPipe GUI libraries directly from Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-21-jdk-headless \
        build-essential \
        gcc \
        g++ \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Create sandbox execution user
RUN useradd -m -u 1000 -s /bin/bash runner

# Set up execution sandbox directory
WORKDIR /workspace
RUN chown -R runner:runner /workspace

WORKDIR /app

# Install Python dependencies
COPY aiml-unified-service/requirements.txt requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy backend files
COPY aiml-unified-service/ .

RUN chown -R runner:runner /app

EXPOSE ${PORT}

# Run FastAPI app with dynamic Render $PORT binding
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]