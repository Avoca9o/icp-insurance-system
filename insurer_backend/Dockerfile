FROM python:3.9

COPY . .

RUN pip install fastapi uvicorn

CMD ["uvicorn", "--app-dir", "src/", "main:app", "--port", "8000"]
