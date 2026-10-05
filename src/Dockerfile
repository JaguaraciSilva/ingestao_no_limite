FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=true

WORKDIR /app

# Copia o requirements da raiz ou da pasta src para dentro do container
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py /app/main.py

ENTRYPOINT ["python", "/app/main.py"]