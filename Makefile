.PHONY: help setup up down test benchmark lint run-backend run-frontend

PYTHON = backend/.venv/bin/python
UVICORN = backend/.venv/bin/uvicorn
PYTEST = backend/.venv/bin/pytest

help:
	@echo "Available commands:"
	@echo "  make setup        - Install backend and frontend dependencies"
	@echo "  make up           - Start all services with Docker Compose"
	@echo "  make down         - Stop all Docker Compose services"
	@echo "  make run-backend  - Run FastAPI backend locally"
	@echo "  make run-frontend - Run Vite frontend locally"
	@echo "  make test         - Run full pytest test suite"
	@echo "  make benchmark    - Run performance benchmark script"

setup:
	uv pip install -r backend/requirements.txt --python $(PYTHON)
	cd frontend && npm install

up:
	docker compose up --build

down:
	docker compose down -v

run-backend:
	cd backend && ../$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 3000

test:
	cd backend && ../$(PYTEST) tests/ -v

benchmark:
	$(PYTHON) scripts/benchmark.py
