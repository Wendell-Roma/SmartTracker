FROM python:3.12-slim

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libssl-dev curl \
    # Dependências do Playwright/Chromium (substitui o --with-deps que quebra no slim)
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 libatspi2.0-0 \
    libx11-6 libxext6 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python primeiro (cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instala apenas o browser (sem --with-deps, pois já instalamos as libs acima)
RUN python -m playwright install chromium

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