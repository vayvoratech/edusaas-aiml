# ----------------------------------------------------------------------
# Stage 1: Pull Java from official Eclipse Temurin 21 image
# ----------------------------------------------------------------------
FROM eclipse-temurin:21-jdk AS java-source

# ----------------------------------------------------------------------
# Stage 2: Pull Python binaries and libraries from official Python image
# ----------------------------------------------------------------------
FROM python:3.12-slim AS python-source

# ----------------------------------------------------------------------
# Stage 3: Final consolidated runtime based on gcc:14
# ----------------------------------------------------------------------
FROM gcc:14

# Prevent interactive prompts during installs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Configure Java environment variables
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Copy OpenJDK from Stage 1
COPY --from=java-source $JAVA_HOME $JAVA_HOME

# Copy Python runtime & standard libraries from Stage 2
COPY --from=python-source /usr/local/bin /usr/local/bin
COPY --from=python-source /usr/local/lib /usr/local/lib
COPY --from=python-source /usr/local/include /usr/local/include

# Refresh dynamic linker cache for Python and GCC runtime libraries
RUN ldconfig

# Create a single sandboxed non-root user
RUN useradd -m -u 1000 -s /bin/bash runner

# Set up isolated workspace directory
WORKDIR /workspace
RUN chown -R runner:runner /workspace

USER runner

CMD ["/bin/bash"]