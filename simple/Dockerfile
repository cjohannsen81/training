FROM python:alpine3.19 
# FROM cgr.dev/chainguard/python:latest-dev

WORKDIR /app

COPY requirements.txt /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

EXPOSE 8000

ENTRYPOINT ["python3"]
CMD ["app.py"]
