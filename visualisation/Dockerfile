FROM python:3-slim

EXPOSE 7070

WORKDIR /src

COPY pyproject.toml .
RUN pip install .[test]

COPY visualisation/src .
COPY visualisation/.streamlit .streamlit

CMD ["streamlit", "run", "main.py", "--browser.gatherUsageStats", "false", "--server.port", "7070", "--server.address", "0.0.0.0"]
