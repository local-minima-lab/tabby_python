# 1. Use a lightweight Python base image
FROM python:3.11-slim

# 2. Set environment variables to optimize Python performance
# Prevents Python from writing .pyc files and keeps stdout/stderr unbuffered
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies (if any are needed for Tabby/OpenAI)
# We use --no-install-recommends to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy only the requirements first to leverage Docker cache
COPY requirements1.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir -r requirements1.txt

# 7. Copy the rest of your application code
# Ensure your .env is EXCLUDED via .dockerignore for security
COPY . .

# 8. Expose the port FastAPI runs on (8080 is the Cloud Run default)
EXPOSE 8080

# 9. Start the application using Uvicorn
# We use 0.0.0.0 to allow external connections and 8080 for Cloud Run compatibility
CMD ["uvicorn", "src.tabby.web.openai_app:app", "--host", "0.0.0.0", "--port", "8080"]