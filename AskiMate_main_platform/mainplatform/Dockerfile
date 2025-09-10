# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FORCE_REBUILD=2025-09-10

# Set working directory
WORKDIR /app

# Install system dependencies (with dos2unix for fixing line endings)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage caching for dependencies
COPY ./AskiMate_main_platform/mainplatform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy manage.py separately and normalize line endings (remove CRLF & BOM)
COPY ./AskiMate_main_platform/mainplatform/manage.py ./manage.py
RUN dos2unix ./manage.py && sed -i '1s/^\xEF\xBB\xBF//' ./manage.py

# Copy the rest of the Django project
COPY ./AskiMate_main_platform/mainplatform/ ./

# Expose port for Render
EXPOSE 8000

# Command is taken from render.yaml
CMD ["gunicorn", "AskiMate_platform.wsgi:application", "--bind", "0.0.0.0:8000"]
