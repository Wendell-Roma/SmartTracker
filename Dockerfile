FROM python:3.12-slim

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libssl-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python primeiro (cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala Playwright e browsers (necessário para sites com JS pesado)
RUN playwright install chromium --with-deps

# Copia o restante do projeto
COPY . .

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=sqlite:///data/prices.db

# Cria pasta de dados persistente
RUN mkdir -p /app/data

EXPOSE 5000

# Por padrão inicia o dashboard + scheduler juntos via entrypoint
CMD ["python", "entrypoint.py"]
