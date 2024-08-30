FROM python:3.12-slim

WORKDIR /app

COPY static/ static/
COPY templates/ templates/
COPY app.py app.py
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]