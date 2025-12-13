# Dockerfile for Cipherlink
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create keys directory (keys should be mounted as volume)
RUN mkdir -p /app/keys

# Expose default server port
EXPOSE 8888

# Default command (can be overridden)
CMD ["python", "scripts/run_server.py", "--host", "0.0.0.0"]

