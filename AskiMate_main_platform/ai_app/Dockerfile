# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies and tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    nano \
    unzip \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements file first for better cache usage
COPY ./AskiMate_main_platform/ai_app/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install AWS CLI and boto3
RUN pip install --no-cache-dir awscli boto3

# Copy the entire AI app source code
COPY ./AskiMate_main_platform/ai_app/ ./

# Expose port for the FastAPI app
EXPOSE 8000

# Start FastAPI with Uvicorn
CMD ["uvicorn", "chat_app:app", "--host", "0.0.0.0", "--port", "8000"]
