FROM python:3.10-slim

# دابەزاندنی ففمپێگ و پێداویستییەکانی تری سیستم
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# کۆپیکردنی هەموو فایلەکان
COPY . .

# دابەزاندنی کتێبخانەکانی ناو ڕیکوایرمێنتس
RUN pip install --no-cache-dir -r requirements.txt

# کارپێکردنی بۆتەکە
CMD ["python", "main.py"]