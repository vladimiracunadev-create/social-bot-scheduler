clean: ## Limpieza estándar (contenedores y volúmenes del proyecto)
	python3 hub.py clean

nuke: ## ☢️ LIMPIEZA TOTAL (Borra TODO: imágenes base, volúmenes, redes y caché)
	docker system prune -a -f --volumes

check: ## Verifica recursos físicos de la máquina (CPU, RAM, Disco)
	python3 check_resources.py

up: ## Levanta la infraestructura con verificación de recursos y todos los servicios (Full)
	python3 hub.py up --full

# ... rest of the file ...

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

deploy: ## Despliega los manifiestos en el clúster de Kubernetes activo
	@echo "☸️ Desplegando en Kubernetes..."
	kubectl apply -k k8s/overlays/prod/ || kubectl apply -f k8s/base/
	@echo "✅ Despliegue solicitado."



demo09: ## Ejecuta la demostraci?n del Caso 09
	@echo "Iniciando Demo Caso 09 (Python -> FastAPI Gateway)..."
	python3 hub.py ejecutar 09-python-to-gateway
