FROM python:3.9-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL="postgresql://postgres:postgres@158.160.79.17:5432/app_db"

WORKDIR /src

RUN apt-get update \
    && apt-get -y install gcc libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

