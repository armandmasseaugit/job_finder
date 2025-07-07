FROM python:3.12-slim

WORKDIR /app

ENV AWS_ACCESS_KEY_ID=changeme
ENV AWS_SECRET_ACCESS_KEY=changeme
ENV AWS_REGION=us-east-1

COPY web_app/backend /app
COPY /conf /app

RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "web_app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
