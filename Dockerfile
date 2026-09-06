# ----------------------------------------------------------------------
# Stage 1: Source Java 21 (Eclipse Temurin)
# ----------------------------------------------------------------------
FROM eclipse-temurin:21-jdk AS java-source

# ----------------------------------------------------------------------
# Stage 2: Source Python 3.12
# ----------------------------------------------------------------------
FROM python:3.12-slim AS python-source

# ----------------------------------------------------------------------
# Stage 3: Source Node.js 20
# ----------------------------------------------------------------------
FROM node:20-bookworm-slim AS node-source

# ----------------------------------------------------------------------
# Stage 4: Final Consolidated Runtime (GCC 14 base)
# ----------------------------------------------------------------------
FROM gcc:14-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Set paths for Java and Node.js
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:/usr/local/node/bin:${PATH}"

# 1. Copy OpenJDK from Stage 1
COPY --from=java-source $JAVA_HOME $JAVA_HOME

# 2. Copy Python 3.12 from Stage 2
COPY --from=python-source /usr/local/bin /usr/local/bin
COPY --from=python-source /usr/local/lib /usr/local/lib
COPY --from=python-source /usr/local/include /usr/local/include

# 3. Copy Node.js from Stage 3
COPY --from=node-source /usr/local /usr/local/node

# Refresh shared library linker cache
RUN ldconfig

# Create sandboxed runner user for untrusted student code execution
RUN useradd -m -u 10001 -s /bin/bash sandboxrunner

# Create execution workspace and sandbox directories
WORKDIR /app
RUN mkdir -p /tmp/sandboxes && chown -R sandboxrunner:sandboxrunner /tmp/sandboxes

# Install Express API dependencies
COPY package*.json ./
RUN npm install --omit=dev

# Copy application backend source files (server.js, src/, etc.)
COPY . .

# Expose Render web port
EXPOSE ${PORT}

# Run the Node.js API server, resolving Render's dynamic $PORT
CMD ["sh", "-c", "node server.js"]