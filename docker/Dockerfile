# AIbasic v1.0 - Docker Image
FROM python:3.11-slim

LABEL maintainer="AIbasic"
LABEL version="1.0"
LABEL description="AIbasic - Natural Language Programming"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY examples/ ./examples/
COPY docs/ ./docs/
COPY README.MD ./
COPY MODULES_GUIDE.md ./
COPY TASK_TYPES.md ./

# Create output directories
RUN mkdir -p /app/output /app/logs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV AIBASIC_HOME=/app

# Create non-root user
RUN useradd -m -u 1000 aibasic && \
    chown -R aibasic:aibasic /app

USER aibasic

# Default command
CMD ["/bin/bash"]
