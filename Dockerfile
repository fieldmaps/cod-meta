FROM python:3.13-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["fastapi", "run", "app", "--port", "80"]
