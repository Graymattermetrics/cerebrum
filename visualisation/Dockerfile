FROM python:3-slim

EXPOSE 7070

WORKDIR /src

COPY pyproject.toml .
RUN pip install .[test]

COPY visualisation/src .

CMD ["streamlit", "run", "main.py", "--server.port", "7070", "--server.address", "0.0.0.0"]
