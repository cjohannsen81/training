# Stage 1: Build
FROM python:3.9 as build

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim as runtime

WORKDIR /app
COPY --from=build /app /app

CMD ["python", "app.py"]
