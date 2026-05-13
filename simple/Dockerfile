FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    flask \
    requests

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
