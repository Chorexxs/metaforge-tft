.PHONY: install dev scrape test lint build docker-up docker-down clean help

help:
	@echo "TFT HUD - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install all dependencies (Python + Node)"
	@echo "  dev          Start development servers"
	@echo "  scrape       Run scrapers manually"
	@echo "  test         Run tests"
	@echo "  lint         Run linters"
	@echo "  build        Build production artifacts"
	@echo "  docker-up    Start Docker services"
	@echo "  docker-down  Stop Docker services"
	@echo "  clean        Clean generated files"

install:
	@echo "Installing Python dependencies..."
	uv sync
	@echo "Installing Node dependencies..."
	cd frontend && npm install
	cd dashboard && npm install

dev:
	@echo "Starting development servers..."
	@echo "Run backend: cd backend && uvicorn main:app --reload"
	@echo "Run scraper (scheduled): python -m scraper.scheduler"

scrape:
	@echo "Running scrapers..."
	python -m scraper.comps_scraper
	python -m scraper.items_scraper
	python -m scraper.augments_scraper

test:
	pytest tests/ -v --cov

lint:
	@echo "Running Python linters..."
	ruff check backend scraper shared
	mypy backend scraper shared
	@echo "Running JavaScript linter..."
	prettier --check "frontend/**/*.{js,jsx,ts,tsx}"
	prettier --check "dashboard/**/*.{js,jsx,ts,tsx}"

build:
	@echo "Building backend..."
	uv build
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Build complete"

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf backend/__pycache__
	rm -rf scraper/__pycache__
	rm -rf shared/__pycache__
	rm -rf tests/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true