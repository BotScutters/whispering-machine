FROM python:3.10-slim

# Install system dependencies for display management
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 display_user && \
    chown -R display_user:display_user /app
USER display_user

# Health check endpoint
EXPOSE 8000

CMD ["python", "app.py"]
