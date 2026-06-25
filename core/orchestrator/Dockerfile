FROM python:3.11-slim

WORKDIR /app

COPY core ./core
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

CMD ["uvicorn", "core.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8002"]