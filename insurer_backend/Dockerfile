FROM python:3.9-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN apt-get update \
    && apt-get -y install gcc libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /src

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8001 > insurer.log 2>&1"]

