FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=true
ENV PYTHONPATH=/app

WORKDIR /app

# Copia o requirements da raiz e instala as dependências
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da raiz (incluindo a pasta src/) para /app
COPY . /app/

ENTRYPOINT ["python", "src/main.py"]