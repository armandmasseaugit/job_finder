FROM python:3.12-slim

WORKDIR /app
COPY web_app/frontend/ /app
COPY /conf /app

RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "web_app/frontend/app.py"]
