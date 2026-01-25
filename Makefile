# Social Bot Scheduler Makefile

# Variables
IMAGE_NAME = social-bot-scheduler
TAG = latest

.PHONY: help install build up down logs deploy k8s-clean

help: ## Muestra este mensaje de ayuda
	@echo "Uso: make [comando]"
	@echo ""
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instala las dependencias locales de Python
	pip install -r requirements.txt

build: ## Construye la imagen de Docker
	docker build -t $(IMAGE_NAME):$(TAG) .

up: ## Levanta el bot usando Docker Compose
	docker-compose up -d

down: ## Detiene los contenedores de Docker Compose
	docker-compose down

logs: ## Muestra los logs del contenedor del bot
	docker-compose logs -f bot

deploy: build ## Despliega en Kubernetes (requiere kubectl configurado)
	kubectl apply -f k8s/configmap.yaml
	@echo "Nota: Asegúrate de haber creado el secret desde k8s/secret.example.yaml"
	kubectl apply -f k8s/cronjob.yaml

k8s-clean: ## Elimina los recursos de Kubernetes del proyecto
	kubectl delete -f k8s/cronjob.yaml
	kubectl delete -f k8s/configmap.yaml
