# Gemini-OpenClaw Gateway Dockerfile
# Follows install.sh installation process

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy parent Gemini-API project
COPY .. /app/Gemini-API

# Set working directory to gateway
WORKDIR /app/Gemini-API/openclaw-gateway

# Upgrade pip (following install.sh)
RUN pip install --upgrade pip

# Install parent Gemini-API project in editable mode (following install.sh)
RUN if [ -f "../pyproject.toml" ]; then \
    pip install -e ..; \
    else \
    pip install 'curl-cffi>=0.7.2' 'loguru>=0.7.3' 'orjson>=3.11.7' 'pydantic>=2.10.5'; \
    fi

# Install gateway dependencies (following install.sh)
RUN pip install --no-cache-dir -r requirements.txt

# Create temp directory (following install.sh)
RUN mkdir -p /tmp/gemini-gateway

# Create .env file placeholder (user must mount their own .env)
RUN touch .env

# Expose port
EXPOSE 18080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:18080/health || exit 1

# Run server directly (not as module since we're in the correct directory)
CMD ["python", "api_server.py"]
