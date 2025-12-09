
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Final image
FROM python:3.11-slim
WORKDIR /app

# Runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 poppler-utils tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user EARLY
RUN useradd -m -s /bin/bash appuser

# Copy packages from builder — BUT CHANGE OWNERSHIP to appuser
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PATH=/root/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser app/templates/ ./templates/
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser repo-to-index/ ./repo-to-index/
COPY --chown=appuser:appuser models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload", "--reload-dir", "/app"]