# 🔍 Price Monitor

> Bot que rastreia preços de produtos em múltiplos e-commerces brasileiros e envia alertas quando o preço alvo é atingido.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-automated-2088FF?style=flat-square&logo=githubactions)

---

## ✨ Funcionalidades

- 🛒 **Suporte a múltiplas lojas**: Mercado Livre (API oficial), Amazon, Magazine Luiza, Americanas e KaBuM
- 📊 **Dashboard web** com histórico de preços em gráfico interativo
- 🔔 **Alertas por e-mail e Telegram** quando o preço cai abaixo da meta
- ⏰ **Agendamento automático** via APScheduler ou GitHub Actions (sem precisar de servidor)
- 🐳 **Docker** para rodar tudo com um comando
- 🖥️ **CLI interativa** para gerenciar produtos pelo terminal

---

## 🏗️ Arquitetura

```
price-monitor/
├── .github/workflows/scraper.yml   # GitHub Actions (roda a cada 6h)
├── app/
│   ├── scrapers/                   # Um scraper por loja
│   │   ├── base.py                 # Classe abstrata + retry lógico
│   │   ├── mercadolivre.py         # Usa API oficial do ML
│   │   ├── amazon.py
│   │   ├── magalu.py
│   │   ├── americanas.py
│   │   └── kabum.py
│   ├── db/
│   │   ├── models.py               # Product + PriceHistory (SQLAlchemy)
│   │   └── database.py
│   ├── notifications/
│   │   ├── email_sender.py         # SMTP via Gmail
│   │   └── telegram_bot.py
│   ├── dashboard/
│   │   ├── app.py                  # Flask app + API REST
│   │   └── templates/              # HTML + Chart.js
│   └── scheduler.py                # APScheduler
├── cli.py                          # CLI com Click + Rich
├── entrypoint.py                   # Dashboard + Scheduler no mesmo processo
├── docker-compose.yml
└── Dockerfile
```

---

## 🚀 Como usar

### Opção 1 — Docker (recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/price-monitor.git
cd price-monitor

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# 3. Suba os containers
docker compose up -d

# 4. Acesse o dashboard
open http://localhost:5000
```

### Opção 2 — Local (Python)

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt
playwright install chromium

# 3. Configure o .env
cp .env.example .env

# 4. Inicie o dashboard + scheduler
python entrypoint.py
```

---

## 🖥️ CLI

```bash
# Adicionar produto para monitorar
python cli.py add "https://www.amazon.com.br/dp/B09XYZ" --price 299.99

# Listar todos os produtos
python cli.py list

# Verificar preços agora (manualmente)
python cli.py check

# Remover produto
python cli.py remove 3

# Iniciar scheduler contínuo
python cli.py run
```

---

## ⚙️ Configuração (.env)

| Variável              | Descrição                                   | Obrigatória |
|-----------------------|---------------------------------------------|-------------|
| `DATABASE_URL`        | URL do banco (SQLite padrão)                | Não         |
| `EMAIL_SENDER`        | Gmail remetente                             | Não         |
| `EMAIL_PASSWORD`      | App Password do Gmail                       | Não         |
| `EMAIL_RECEIVER`      | E-mail destinatário dos alertas             | Não         |
| `TELEGRAM_TOKEN`      | Token do bot no @BotFather                  | Não         |
| `TELEGRAM_CHAT_ID`    | ID do seu chat com o bot                    | Não         |
| `CHECK_INTERVAL_HOURS`| Intervalo entre verificações (padrão: 6)    | Não         |
| `ML_APP_ID`           | Client ID da API Mercado Livre              | Não         |

> 💡 Nenhuma variável é obrigatória para rodar — as notificações são ignoradas se não configuradas.

---

## 🤖 GitHub Actions (sem servidor!)

O workflow `.github/workflows/scraper.yml` roda automaticamente a cada 6 horas usando os runners gratuitos do GitHub.

**Como configurar:**

1. Vá em **Settings → Secrets and variables → Actions** no seu repositório
2. Adicione os secrets: `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVER`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
3. O banco de dados é preservado entre execuções via cache do Actions

---

## 🧪 Testes

```bash
pytest tests/ -v
```

---

## 🛒 Lojas suportadas

| Loja            | Método           | Observações                        |
|-----------------|------------------|------------------------------------|
| Mercado Livre   | API oficial      | Mais estável, não requer auth      |
| Amazon BR       | BeautifulSoup    | Pode exigir headers específicos    |
| Magazine Luiza  | JSON-LD + HTML   | Dados estruturados no HTML         |
| Americanas      | JSON-LD + HTML   | Idem                               |
| KaBuM           | BeautifulSoup    | HTML limpo, fácil de parsear       |

---

## 📄 Licença

MIT — use, modifique e distribua à vontade.
