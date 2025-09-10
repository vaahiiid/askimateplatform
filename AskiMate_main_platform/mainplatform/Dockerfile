# Base image
FROM python:3.11-slim

# Environment variables (FORCE_REBUILD تغییر بده هر بار که میخوای کش شکسته شه)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FORCE_REBUILD=2025-09-10-3

# Set working directory
WORKDIR /app

# Install system dependencies (add dos2unix and file for debugging line endings)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    file \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage caching for dependencies
COPY ./AskiMate_main_platform/mainplatform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy manage.py separately and normalize line endings (remove CRLF & BOM)
COPY ./AskiMate_main_platform/mainplatform/manage.py ./manage.py
RUN file ./manage.py && \
    head -n 2 ./manage.py && \
    dos2unix ./manage.py && \
    sed -i '1s/^\xEF\xBB\xBF//' ./manage.py && \
    file ./manage.py && \
    head -n 2 ./manage.py

# Copy the rest of the Django project
COPY ./AskiMate_main_platform/mainplatform/ ./

# Expose port for Render
EXPOSE 8000

# Default command (as per render.yaml)
CMD ["gunicorn", "AskiMate_platform.wsgi:application", "--bind", "0.0.0.0:8000"]
