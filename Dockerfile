# ----------------------------------------------------------------------
# Stage 1: Source Java 21 (Eclipse Temurin)
# ----------------------------------------------------------------------
FROM eclipse-temurin:21-jdk AS java-source

# ----------------------------------------------------------------------
# Stage 2: Source Python 3.12
# ----------------------------------------------------------------------
FROM python:3.12-slim AS python-source

# ----------------------------------------------------------------------
# Stage 3: Final Consolidated Runtime (GCC 14 base)
# ----------------------------------------------------------------------
FROM gcc:14-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Set Java environment variables
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# 1. Copy OpenJDK from Stage 1
COPY --from=java-source $JAVA_HOME $JAVA_HOME

# 2. Copy Python 3.12 from Stage 2
COPY --from=python-source /usr/local/bin /usr/local/bin
COPY --from=python-source /usr/local/lib /usr/local/lib
COPY --from=python-source /usr/local/include /usr/local/include

# Refresh shared library linker cache for Python & GCC
RUN ldconfig

# Create sandboxed runner user
RUN useradd -m -u 10001 -s /bin/bash sandboxrunner

# Create execution workspace and sandbox directories
WORKDIR /app
RUN mkdir -p /tmp/sandboxes && chown -R sandboxrunner:sandboxrunner /tmp/sandboxes

# Copy existing project files (no extra files created)
COPY . .

# Expose Render web port
EXPOSE ${PORT}

# Run built-in Python HTTP server to satisfy Render health check
CMD ["sh", "-c", "python3 -m http.server ${PORT} --bind 0.0.0.0"]