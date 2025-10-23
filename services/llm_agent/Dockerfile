FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 llm_user && \
    chown -R llm_user:llm_user /app
USER llm_user

# Health check endpoint
EXPOSE 8000

CMD ["python", "app.py"]
