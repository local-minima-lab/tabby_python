# STAGE 1: Builder (The "Kitchen")
# We install all compilers here to build the fast 'uvloop' for uvicorn
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools needed for high-performance Python extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies to a temporary folder (/install)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---

# STAGE 2: Runner (The "Serving Plate")
# This is the actual image that gets deployed. It contains NO compilers.
FROM python:3.11-slim

WORKDIR /app

# 1. Copy only the installed packages from the builder
COPY --from=builder /install /usr/local

# 2. Copy your source code and configs
# We copy 'src' and 'configs' to keep the structure clean
COPY src/ ./src/
COPY configs/ ./configs/

# 3. Critical Environment Variables
# PYTHONPATH tells Python that your 'tabby' package lives inside the 'src' folder
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 4. Handle the Cloud Run Port
# Cloud Run injects a $PORT variable. This shell command ensures uvicorn listens to it.
ENV PORT=8080
CMD ["uvicorn", "src.tabby.web.openai_app:app", "--host", "0.0.0.0", "--port", "8080"]