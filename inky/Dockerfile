# Build
FROM cgr.dev/chainguard/python:latest-dev AS builder

ENV LANG=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/inky/venv/bin:$PATH"

WORKDIR /inky

USER root

RUN apk update && apk add curl
RUN curl --version

RUN python -m venv /inky/venv
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Runtime
FROM cgr.dev/chainguard/python:latest

WORKDIR /inky

ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

COPY inky.py inky.png ./
COPY --from=builder /inky/venv /venv

ENTRYPOINT [ "python", "/inky/inky.py" ]

