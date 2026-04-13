FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
RUN uv sync --no-install --frozen

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
COPY pyproject.toml ./

RUN uv sync --frozen

COPY backend/ /app/backend/
COPY scraper/ /app/scraper/
COPY shared/ /app/shared/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]