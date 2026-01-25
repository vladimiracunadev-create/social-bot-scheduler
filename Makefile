# Social Bot Scheduler Makefile

# Variables
IMAGE_NAME = social-bot-scheduler
TAG = latest

.PHONY: help install build up down logs deploy k8s-clean

help: ## Muestra este mensaje de ayuda
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Python Development ---
install: ## Instala las dependencias locales de Python (Dev)
	pip install -r requirements.txt
	pip install black flake8 pre-commit pytest pytest-cov mypy types-requests

test: ## Ejecuta las pruebas unitarias
	pytest --cov=src/social_bot tests/

lint: ## Ejecuta el linter (flake8 y black)
	black --check .
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

format: ## Formatea el código automáticamente con black
	black .

setup-pc: ## Configura los git hooks de pre-commit
	pre-commit install

# --- Docker & Cases ---
up: ## Levanta todo el entorno (Cuidado: consume mucha memoria)
	docker-compose up -d

down: ## Detiene todos los contenedores
	docker-compose down

up-case-01: ## Levanta Caso 01: Python -> PHP
	docker-compose up -d n8n dest-php

up-case-02: ## Levanta Caso 02: Python -> Go
	docker-compose up -d n8n dest-go

up-case-03: ## Levanta Caso 03: Go -> Node.js
	docker-compose up -d n8n dest-node

up-case-04: ## Levanta Caso 04: Node.js -> FastAPI
	docker-compose up -d n8n dest-fastapi

up-case-05: ## Levanta Caso 05: Laravel -> React
	docker-compose up -d n8n dest-react

up-case-06: ## Levanta Caso 06: Go -> Symfony
	docker-compose up -d n8n dest-symfony

up-case-07: ## Levanta Caso 07: Rust -> Ruby
	docker-compose up -d n8n dest-ruby

up-case-08: ## Levanta Caso 08: C# -> Flask
	docker-compose up -d n8n dest-flask

logs: ## Muestra logs generales
	docker-compose logs -f

logs-n8n: ## Muestra logs de n8n
	docker-compose logs -f n8n

# --- Kubernetes ---
deploy: build ## Despliega en Kubernetes (requiere kubectl)
	kubectl apply -f k8s/configmap.yaml
	@echo "Nota: Asegúrate de haber creado el secret desde k8s/secret.example.yaml"
	kubectl apply -f k8s/cronjob.yaml

k8s-clean: ## Elimina los recursos de Kubernetes
	kubectl delete -f k8s/cronjob.yaml
	kubectl delete -f k8s/configmap.yaml
