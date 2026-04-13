FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir telethon pytz python-socks[asyncio]
CMD ["python", "main.py"]
