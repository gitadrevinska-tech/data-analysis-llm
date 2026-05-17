FROM python:3.11-slim

WORKDIR /app/ui

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ ./templates/

CMD ["python", "/app/ui/app.py"]