FROM python:3-slim

EXPOSE 6060

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml . 
RUN pip install --no-cache-dir .[test]

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:6060", "-k", "uvicorn.workers.UvicornWorker", "--chdir", "app", "main:app"]
