# Makefile Centralizado - Social Bot Scheduler

.PHONY: help doctor up down logs logs-n8n scan demo setup-n8n smoke reset-n8n

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
	trivy image social-bot-scheduler:3.0.0

demo: ## Ejecuta una demostración rápida (Caso 01)
	@echo "🚀 Iniciando Demo Caso 01 (Python -> PHP)..."
	python3 hub.py ejecutar 01-python-to-php

setup-n8n: ## Info sobre la auto-configuración de n8n
	@echo "⚙️  n8n se auto-configura al arrancar con 'make up'"
	@echo "📋 Workflows en: n8n/workflows/"
	@echo "🔑 Credenciales: admin@social-bot.local / SocialBot2026!"
	@echo "🌐 UI: http://localhost:5678"

smoke: ## Verifica que los servicios principales estén vivos
	@echo "🔍 Verificando servicios Docker..."
	@docker-compose ps
	@echo ""
	@echo "🔗 Probando n8n health..."
	@wget -q --spider http://localhost:5678/healthz 2>/dev/null && echo "✅ n8n OK" || echo "⚠️  n8n no responde (puede estar arrancando, espera 30s)"

reset-n8n: ## Fuerza re-importación de workflows en el próximo arranque
	@echo "🔄 Eliminando marcador de importación..."
	docker-compose exec n8n rm -f /home/node/.n8n/.workflows_imported
	@echo "🔁 Reiniciando n8n..."
	docker-compose restart n8n
	@echo "✅ n8n re-importará workflows al arrancar"

