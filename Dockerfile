FROM python:3.9-alpine

WORKDIR ~/bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r ./requirements.txt

COPY bot ./bot

CMD ["python", "-m", "app"]