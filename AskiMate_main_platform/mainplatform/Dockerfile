# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FORCE_REBUILD=2025-09-13-1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    file \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# مسیر requirements.txt رو از ریشه صحیح بگیریم
COPY ./AskiMate_main_platform/mainplatform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY ./AskiMate_main_platform/mainplatform/ ./

# Normalize manage.py
RUN dos2unix ./manage.py && \
    sed -i '1s/^\xEF\xBB\xBF//' ./manage.py && \
    echo '#!/usr/bin/env python3' | cat - ./manage.py > temp && mv temp ./manage.py && \
    chmod +x ./manage.py && \
    echo "---- manage.py (before run) ----" && \
    file ./manage.py && \
    head -n 2 ./manage.py && \
    echo "--------------------------------"

# Expose port
EXPOSE 8000

# Final run command
CMD sh -c "python3 manage.py migrate && \
           python3 manage.py collectstatic --noinput && \
           gunicorn AskiMate_platform.wsgi:application --bind 0.0.0.0:8000"
