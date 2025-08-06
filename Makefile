.PHONY: help install run test clean docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  make install      Install dependencies"
	@echo "  make run          Run the application locally"
	@echo "  make test         Run tests"
	@echo "  make clean        Clean up cache files"
	@echo "  make docker-up    Start Docker containers"
	@echo "  make docker-down  Stop Docker containers"
	@echo "  make migrate      Run database migrations"

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v

migrate:
	docker-compose exec db psql -U postgres -d face_recognition -f /docker-entrypoint-initdb.d/init.sql

logs:
	docker-compose logs -f app

shell:
	docker-compose exec app /bin/bash