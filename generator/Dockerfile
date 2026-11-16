FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir httpx

COPY generator.py .

CMD ["python", "generator.py"]