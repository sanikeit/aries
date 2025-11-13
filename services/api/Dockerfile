FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy monorepo structure for shared packages
COPY ./packages/schemas /packages/schemas
COPY ./services/api/requirements.txt .

# Install Python dependencies including shared packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e /packages/schemas

# Copy application code
COPY ./services/api/app /app

# Create non-root user for security
RUN useradd -m -u 1000 aries && chown -R aries:aries /app
USER aries

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]