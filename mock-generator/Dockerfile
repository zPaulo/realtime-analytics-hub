FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY mock-generator/pyproject.toml ./mock-generator/

RUN uv sync --frozen --package mock-generator --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY mock-generator/ ./mock-generator/

WORKDIR /app/mock-generator

CMD ["python", "generator.py"]