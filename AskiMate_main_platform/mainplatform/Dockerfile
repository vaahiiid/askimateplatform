# ------------------------
# ۱) Base image سبک و امن
# ------------------------
FROM python:3.11-slim

# ------------------------
# ۲) تنظیمات محیط
# ------------------------
# PYTHONDONTWRITEBYTECODE = جلوگیری از ساخت pyc
# PYTHONUNBUFFERED = خروجی فوری در لاگ
# FORCE_REBUILD = تغییر عددش کش Render رو میشکنه
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FORCE_REBUILD=2025-09-13-2

# ------------------------
# ۳) دایرکتوری کاری در کانتینر
# ------------------------
WORKDIR /app

# ------------------------
# ۴) نصب وابستگی‌های سیستمی
# ------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    file \
    && rm -rf /var/lib/apt/lists/*

# ------------------------
# ۵) کپی و نصب requirements
# ------------------------
COPY AskiMate_main_platform/mainplatform/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# ------------------------
# ۶) کپی تمام پروژه
# ------------------------
# محتویات mainplatform میره داخل /app
COPY AskiMate_main_platform/mainplatform/ /app/

# ------------------------
# ۷) آماده‌سازی manage.py
# ------------------------
RUN dos2unix manage.py && \
    sed -i '1s/^\xEF\xBB\xBF//' manage.py && \
    echo '#!/usr/bin/env python3' | cat - manage.py > temp && mv temp manage.py && \
    chmod +x manage.py && \
    echo "---- manage.py (before run) ----" && \
    file manage.py && \
    head -n 2 manage.py && \
    echo "--------------------------------"

# ------------------------
# ۸) اکسپوز کردن پورت HTTP
# ------------------------
EXPOSE 8000

# ------------------------
# ۹) اجرای کانتینر
# ------------------------
CMD sh -c "python3 manage.py migrate && \
           python3 manage.py collectstatic --noinput && \
           gunicorn AskiMate_platform.wsgi:application --bind 0.0.0.0:8000"
