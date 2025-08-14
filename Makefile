.PHONY: help run dev install clean test logs

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make run      - Run the worker locally"
	@echo "  make dev      - Run with docker-compose"
	@echo "  make clean    - Clean up containers"
	@echo "  make test     - Run tests"
	@echo "  make logs     - Show worker logs"

install:
	pip install -r requirements.txt

run:
	python -m app.main

dev:
	docker compose up --build

dev-detached:
	docker compose up -d --build

down:
	docker compose down

clean:
	docker compose down -v

logs:
	docker compose logs -f face-recognition-worker

rebuild:
	docker compose build --no-cache face-recognition-worker
	docker compose up

db-reset:
	docker compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS face_recognition_local;"
	docker compose exec db psql -U postgres -c "CREATE DATABASE face_recognition_local;"
	docker compose restart face-recognition-worker