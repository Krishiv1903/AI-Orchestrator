FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core ./core
COPY tools ./tools

EXPOSE 10000

CMD ["sh", "-c", "uvicorn core.deployment:app --host 0.0.0.0 --port ${PORT:-10000}"]
