# Base Image: Python 3.10 slim variant for a smaller footprint
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set timezone
ENV TZ=Asia/Taipei

# Install system dependencies (for PyPDF and others)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    --no-install-recommends \
    # Clean up
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python packages
# Added fastapi, uvicorn, pydantic-settings, apscheduler
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn pydantic-settings apscheduler

# Copy source code
COPY ./src /app/src

# Create necessary directories
RUN mkdir -p /app/downloads /app/generated_documents /app/logs

# Expose FastAPI port
EXPOSE 8000

# Run Uvicorn targeting the FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
