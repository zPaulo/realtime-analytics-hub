# 1. Base Image
FROM python:3.12-slim

# 2. Instala o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Define diretório de trabalho na raiz do container
WORKDIR /app

# 4. Copia os arquivos de definição de dependência da RAIZ e do BACKEND
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml ./backend/

# 5. Instalação das dependências do BACKEND
# --package backend: Instala só o necessário para o Django
RUN uv sync --frozen --package backend --no-install-project

# 6. Adiciona o venv ao PATH
ENV PATH="/app/.venv/bin:$PATH"

# 7. Copia o código fonte do backend
COPY backend/ ./backend/

# 8. Define o diretório de execução
WORKDIR /app/backend

# 9. Comando de execução (Daphne para WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]