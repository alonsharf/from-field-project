# Multi-stage Dockerfile for From Field to You application
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Fetch Amazon RDS global CA bundle for SSL verification
RUN curl -sSL https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /etc/ssl/certs/aws-rds-global-bundle.pem

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose ports for both FastAPI and Streamlit
EXPOSE 8000 8501

# Default command runs FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]