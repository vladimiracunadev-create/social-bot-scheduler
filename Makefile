# Makefile Centralizado - Social Bot Scheduler

.PHONY: help doctor up down logs logs-n8n scan

help: ## Muestra este mensaje de ayuda
	@echo "🤖 Social Bot Scheduler - Comandos Disponibles"
	@echo "---------------------------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

doctor: ## Diagnostica el estado del sistema (contenedores, red, archivos)
	python3 hub.py doctor

up: ## Levanta toda la infraestructura (Docker Compose)
	docker-compose up -d

down: ## Detiene y elimina contenedores
	docker-compose down

logs: ## Muestra logs de todos los contenedores en tiempo real
	docker-compose logs -f

logs-n8n: ## Muestra solo los logs de n8n
	docker-compose logs -f n8n

stop: ## Detiene los contenedores sin eliminarlos
	docker-compose stop

restart: ## Reinicia los contenedores
	docker-compose restart

scan: ## Escanea vulnerabilidades en la imagen Docker (requiere Trivy)
	trivy image social-bot-scheduler:2.3.0
