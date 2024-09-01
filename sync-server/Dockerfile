
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gcc \
        curl \
        ca-certificates

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

#TODO: stages, and a seperate stage for dockerized / ci testing

CMD ["python", "/app/src/main.py"]