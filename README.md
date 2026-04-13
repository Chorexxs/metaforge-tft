# TFT HUD

Asistente de Draft en Tiempo Real para Teamfight Tactics.

## Estructura del Proyecto

```
├── backend/         # FastAPI backend
├── frontend/        # Electron overlay HUD
├── scraper/        # Scrapers de meta y compos
├── shared/         # Modelos y utilidades compartidas
├── scripts/        # Scripts de utilidad
├── tests/          # Pruebas
├── plan.md         # Plan completo del proyecto
└── README.md
```

## Setup

```bash
# Instalar uv (si no lo tienes)
irm https://astral.sh/uv/install.ps1 | iex

# Instalar dependencias Python
uv sync

# Instalar dependencias Node
cd frontend && npm install

# Copiar configuración
cp .env.example .env

# Configurar tu RIOT_API_KEY en .env
```

## Comandos

```bash
# Desarrollo backend
uv run uvicorn backend.main:app --reload

# Desarrollo frontend (Electron)
cd frontend && npm run dev

# Tests
uv run pytest tests/ -v

# Lint
uv run ruff check backend scraper shared
```

## Docker

```bash
docker-compose up -d
```
