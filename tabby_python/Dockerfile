# 1. Use NVIDIA CUDA base for GPU support
# Using Ubuntu 22.04 + CUDA 12.1 which is highly compatible with vLLM 0.15.1
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# 2. Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# 3. Install Python 3.11 and system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Ensure 'python' and 'pip' point to python3.11
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    python3 -m pip install --upgrade pip

# 5. Install dependencies
# We copy this first to leverage Docker's layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the source code
# This copies everything in tabby_python/ into /app in the container
COPY . .

# 7. Set the PYTHONPATH so the 'tabby' module is discoverable
ENV PYTHONPATH=/app/src

# 8. Start the server
# Cloud Run automatically injects the $PORT variable (usually 8080)
CMD uvicorn tabby.web.app:app --host 0.0.0.0 --port $PORT