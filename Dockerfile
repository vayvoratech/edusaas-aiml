FROM gcc:14-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install Java 21 and Python directly from Debian repositories
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jdk-headless \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Create sandboxed runner user
RUN useradd -m -u 10001 -s /bin/bash sandboxrunner

# Create workspace and sandbox directories
WORKDIR /app
RUN mkdir -p /tmp/sandboxes && chown -R sandboxrunner:sandboxrunner /tmp/sandboxes

# Copy project files
COPY . .

# Expose Render web port
EXPOSE ${PORT}

# Run built-in HTTP server on Render's dynamic port
CMD ["sh", "-c", "python3 -m http.server ${PORT} --bind 0.0.0.0"]