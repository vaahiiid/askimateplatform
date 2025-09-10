# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements first to keep Docker layer cache
COPY ./AskiMate_main_platform/mainplatform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the full Django project
COPY ./AskiMate_main_platform/mainplatform/ ./

# Collect static files (without running migrations)
RUN python manage.py collectstatic --noinput || echo "Skipping collectstatic"

# Expose port for Render
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "AskiMate_platform.wsgi:application", "--bind", "0.0.0.0:8000"]
