# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to take advantage of layer caching
COPY ./AskiMate_main_platform/mainplatform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy manage.py separately and fix line endings
COPY ./AskiMate_main_platform/mainplatform/manage.py ./manage.py
RUN dos2unix ./manage.py

# Copy the rest of the Django project
COPY ./AskiMate_main_platform/mainplatform/ ./

# Expose port for Render
EXPOSE 8000

# Final command from render.yaml
CMD ["gunicorn", "AskiMate_platform.wsgi:application", "--bind", "0.0.0.0:8000"]
