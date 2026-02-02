FROM python:3.11-slim

WORKDIR /app

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend /app/backend

# Copy frontend code and build
COPY frontend /app/frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Move back to app directory
WORKDIR /app

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run initialization script and start server
CMD python -m backend.seed_data && uvicorn backend.main:app --host 0.0.0.0 --port 8000
