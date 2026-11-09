FROM python:3.14-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends iproute2 netcat-openbsd openssl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY detect_bola.py .

EXPOSE 443

CMD ["sh", "-c", "openssl req -x509 -newkey rsa:2048 -nodes -keyout /tmp/esm.key -out /tmp/esm.crt -days 1 -subj '/CN=esm-web01' >/dev/null 2>&1 && exec uvicorn main:app --host 0.0.0.0 --port 443 --ssl-keyfile /tmp/esm.key --ssl-certfile /tmp/esm.crt"]
