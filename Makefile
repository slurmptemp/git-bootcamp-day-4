.PHONY: help install run test build up down logs clean

VENV := .venv
PYTHON3 ?= python3
PYTHON ?= $(VENV)/bin/python
PIP := $(PYTHON) -m pip
STAMP_INSTALL := .stamp-install

help:
	@echo "Команды:"
	@echo "  make install   — venv + pip install -r requirements.txt"
	@echo "  make run       — install + запуск локально (python -m webapp)"
	@echo "  make test      — install + pytest"
	@echo "  make build     — собрать docker-образ"
	@echo "  make up        — build + поднять docker-compose"
	@echo "  make down      — остановить docker-compose"
	@echo "  make logs      — логи сервиса web"
	@echo "  make clean     — БД, venv, кэши, docker-контейнеры и образы проекта"

$(VENV)/bin/python:
	$(PYTHON3) -m venv $(VENV)

$(STAMP_INSTALL): requirements.txt $(VENV)/bin/python
	$(PIP) install -r requirements.txt
	@touch $(STAMP_INSTALL)

install: $(STAMP_INSTALL)

run: install
	$(PYTHON) -m webapp

test: install
	$(PYTHON) -m pytest -q

build:
	docker compose build

up: build
	docker compose up -d
	@echo "Открыто на http://localhost:8000"

down:
	docker compose down

logs:
	docker compose logs -f web

clean:
	rm -f data/notes.db data/notes.db-journal
	rm -f $(STAMP_INSTALL)
	rm -rf .pytest_cache $(VENV) venv
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	docker compose down --rmi local --remove-orphans 2>/dev/null || true
