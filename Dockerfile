FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10

RUN apk update
RUN apk add --no-cache python3-dev openssl-dev libffi-dev gcc g++ musl-dev zlib-dev jpeg-dev openjpeg-dev

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app/
ENV PYTHONPATH=/app
EXPOSE 80