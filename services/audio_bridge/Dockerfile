FROM python:3.10-slim

# Install system dependencies for audio and build tools
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    curl \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 audio_user && \
    chown -R audio_user:audio_user /app
USER audio_user

# Health check endpoint
EXPOSE 8000

CMD ["python", "app.py"]
