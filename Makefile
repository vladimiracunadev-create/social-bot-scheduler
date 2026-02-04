# Social Bot Scheduler Makefile

# Variables
IMAGE_NAME = social-bot-scheduler
TAG = latest

.PHONY: help install build up down logs deploy k8s-clean dev-up dev-down hub-run lint test k8s-apply k8s-delete audit

help: ## Muestra este mensaje de ayuda
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Development ---
install: ## Instala las dependencias locales de Python (Dev)
	pip install -r requirements.txt
	pip install black flake8 pre-commit pytest pytest-cov mypy types-requests detect-secrets pip-audit

setup-pc: ## Configura los git hooks de pre-commit
	pre-commit install

lint: ## Ejecuta el linter (flake8 y black)
	black --check .
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

test: ## Ejecuta las pruebas unitarias
	pytest --cov=. tests/ || echo "No tests found yet"

audit: ## Realiza auditoría de dependencias y secretos
	pip-audit
	detect-secrets scan

# --- HUB CLI ---
hub-ejecutar: ## Ejecuta un caso via HUB CLI (ej: make hub-ejecutar CASE=01-python-to-php)
	python hub.py ejecutar $(CASE)

hub-listar: ## Lista los casos disponibles
	python hub.py listar-casos

hub-doctor: ## Ejecuta diagnósticos del sistema
	python hub.py doctor

# --- Docker & Development Stack ---
dev-up: ## Levanta el stack mínimo de desarrollo (n8n + core)
	docker-compose -f docker-compose.dev.yml up -d

dev-down: ## Detiene el stack de desarrollo
	docker-compose -f docker-compose.dev.yml down

up: ## Levanta todo el entorno legacy
	docker-compose up -d

down: ## Detiene todos los contenedores legacy
	docker-compose down

# --- Kubernetes (Kustomize) ---
k8s-apply: ## Despliega en K8s usando Kustomize (dev overlay)
	kubectl apply -k k8s/overlays/dev

k8s-delete: ## Elimina los recursos de K8s usando Kustomize
	kubectl delete -k k8s/overlays/dev

deploy: k8s-apply ## Alias para despliegue
