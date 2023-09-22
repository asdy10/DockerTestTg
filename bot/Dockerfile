FROM python:3.9
WORKDIR /bot
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && chmod 755 .
COPY . .
CMD ["python3", "-u", "app.py"]
