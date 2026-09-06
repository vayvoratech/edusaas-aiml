# ----------------------------------------------------------------------
# Stage 1: Pull Java 21 from official Eclipse Temurin image (Bookworm base)
# ----------------------------------------------------------------------
FROM eclipse-temurin:21-jdk-bookworm AS java-source

# ----------------------------------------------------------------------
# Stage 2: Unified Runtime (Python 3.13 + GCC/G++ + Temurin OpenJDK 21)
# ----------------------------------------------------------------------
FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

# 1. Configure Java environment variables
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# 2. Copy OpenJDK from Stage 1
COPY --from=java-source $JAVA_HOME $JAVA_HOME

# 3. Install GCC, G++, build utilities, and OpenCV/MediaPipe GUI/system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# 4. Create an isolated runner user for sandbox execution
RUN useradd -m -u 1000 -s /bin/bash runner

# 5. Set up workspace and application directories
WORKDIR /workspace
RUN chown -R runner:runner /workspace

WORKDIR /app

# 6. Install Python dependencies
COPY aiml-unified-service/requirements.txt requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt

# 7. Copy backend application files
COPY aiml-unified-service/ .

# Ensure app directory permissions
RUN chown -R runner:runner /app

EXPOSE ${PORT}

# Dynamic port binding for Render ($PORT) with fallback to 8000
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT}"]