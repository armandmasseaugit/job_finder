FROM python:3.12-slim

WORKDIR /app

COPY . /app


RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    make install

EXPOSE 8000

CMD ["bash"]
