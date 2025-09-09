FROM python:3.9-slim

# 1️⃣ ست کردن دایرکتوری کاری
WORKDIR /app

# 2️⃣ نصب دیپندنسی‌های سیستمی و curl برای healthcheck
# - apt-clean برای کم کردن حجم ایمیج
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    nano \
    unzip \
 && rm -rf /var/lib/apt/lists/*

# 3️⃣ کپی requirements.txt برای استفاده از کش لایه‌ها
COPY requirements.txt .

# 4️⃣ نصب پکیج‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ نصب AWS CLI + boto3 فقط یکبار (برای Bedrock/AWS تست)
RUN pip install --no-cache-dir awscli boto3

# 6️⃣ کپی کل سورس برنامه
COPY . .

# 7️⃣ پورت اپ
EXPOSE 8000

# 8️⃣ اجرای پیش‌فرض (FastAPI با Uvicorn)
CMD ["uvicorn", "chat_app:app", "--host", "0.0.0.0", "--port", "8000"]
