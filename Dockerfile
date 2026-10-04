# Stage 1: Build the React frontend
FROM node:20-alpine AS build-frontend
WORKDIR /workspace/app
COPY app/package.json app/package-lock.json ./
RUN npm ci
COPY app/ ./
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.11-slim
WORKDIR /workspace

# Install required system packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (API and models)
COPY . /workspace/

# Copy built frontend from Stage 1
COPY --from=build-frontend /workspace/app/dist /workspace/app/dist

# Expose port for production
EXPOSE 7860

# Run Uvicorn server
CMD ["python", "-m", "uvicorn", "--app-dir", "src", "speechcoach.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
