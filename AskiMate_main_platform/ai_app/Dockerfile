FROM python:3.9-slim

# Set working dir
WORKDIR /app

# Install system dependencies just in case
RUN apt-get update && apt-get install -y gcc

# Copy the requirements.txt first
COPY requirements.txt .

# Install python dependencies (rasa is heavier, so separate for layer caching)
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Make sure your Rasa model is at /app/models
# (COPY models/ models/ or do a volume mount at runtime)

# Expose port for FastAPI
EXPOSE 8000

# Run the app
CMD ["uvicorn", "chat_app:app", "--host", "0.0.0.0", "--port", "8000"]
