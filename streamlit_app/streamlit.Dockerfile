FROM python:3.12-slim

WORKDIR /app

COPY ./streamlit_app/ /app
COPY ./conf/ /app

RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install -r app_requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
