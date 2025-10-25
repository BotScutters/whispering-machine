FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create user
RUN useradd -m -u 1000 mock_user && \
    chown -R mock_user:mock_user /app

USER mock_user

CMD ["python", "app.py"]
