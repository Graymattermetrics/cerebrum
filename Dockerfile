FROM python:3-slim

EXPOSE 6060

WORKDIR /app

COPY pyproject.toml .
RUN pip install .[test]

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:6060", "-k", "uvicorn.workers.UvicornWorker", "--chdir", "app", "main:app"]
