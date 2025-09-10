# Base image
FROM python:3.11-slim

# Environment variables
# FORCE_REBUILD را هر بار که می‌خواهی کش بیلد شکسته شود تغییر بده
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FORCE_REBUILD=2025-09-10-6

# Set working directory
WORKDIR /app

# Install dependencies: build tools, PostgreSQL libs, dos2unix for CRLF→LF, file for debug
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    file \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better caching
COPY ./AskiMate_main_platform/mainplatform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy full Django project
COPY ./AskiMate_main_platform/mainplatform/ ./

# Normalize manage.py inside container to avoid BOM/CRLF issues
RUN dos2unix ./manage.py && \
    sed -i '1s/^\xEF\xBB\xBF//' ./manage.py && \
    echo '#!/usr/bin/env python3' | cat - ./manage.py > temp && mv temp ./manage.py && \
    chmod +x ./manage.py && \
    echo "---- manage.py (before run) ----" && \
    file ./manage.py && \
    head -n 2 ./manage.py && \
    echo "--------------------------------"

# Expose HTTP port for Render/Gunicorn
EXPOSE 8000

# Run Gunicorn server directly
CMD ["gunicorn", "AskiMate_platform.wsgi:application", "--bind", "0.0.0.0:8000"]
