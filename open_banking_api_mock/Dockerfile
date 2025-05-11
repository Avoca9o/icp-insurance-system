FROM python:3.9-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY="secret_key"

WORKDIR /app

RUN apt-get update \
    && apt-get -y install gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 > mock.log 2>&1"]
