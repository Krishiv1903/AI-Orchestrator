FROM python:3.11-slim

WORKDIR /app

COPY tools ./tools
COPY core ./core
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9001 9002 9003 9004

CMD bash -c "\
uvicorn tools.coding_tool.main:app --host 0.0.0.0 --port 9001 & \
uvicorn tools.research_tool.main:app --host 0.0.0.0 --port 9002 & \
uvicorn tools.db_tool.main:app --host 0.0.0.0 --port 9003 & \
uvicorn tools.qa_tool.main:app --host 0.0.0.0 --port 9004 & \
wait"