FROM python:3.12-slim

WORKDIR /app

COPY . /app

ENV PYTHONPATH=.

RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install -r web_app/backend/requirements.txt

EXPOSE 8000

CMD ["uvicorn", "web_app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
