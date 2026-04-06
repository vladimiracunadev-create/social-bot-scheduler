clean: ## Limpieza estandar (contenedores y volumenes del proyecto)
	python3 hub.py clean

nuke: ## LIMPIEZA TOTAL (borra todo: imagenes base, volumenes, redes y cache)
	docker system prune -a -f --volumes

check: ## Verifica recursos fisicos de la maquina (CPU, RAM, Disco)
	python3 check_resources.py

up: ## Levanta la demo completa del laboratorio (perfil full)
	python3 hub.py up --full

up-secure: ## Levanta el modo secure-default (n8n + dashboard maestro + perfiles explicitos)
	docker-compose up -d

up-observability: ## Activa Prometheus, Grafana y cAdvisor solo para analisis local
	docker-compose --profile observability up -d prometheus grafana cadvisor

up-edge: ## Activa el reverse proxy HTTPS/basicauth opcional (requiere EDGE_BASIC_AUTH_HASH)
	python3 hub.py up --edge

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

demo: ## Ejecuta una demostracion rapida (Caso 01)
	@echo "Iniciando demo Caso 01 (Python -> PHP)..."
	python3 hub.py ejecutar 01-python-to-php

setup-n8n: ## Info sobre la auto-configuracion de n8n
	@echo "n8n se auto-configura al arrancar con 'make up' o 'make up-secure'"
	@echo "Workflows en: n8n/workflows/"
	@echo "Credenciales: definidas por N8N_OWNER_EMAIL y N8N_OWNER_PASSWORD en .env"
	@echo "UI: http://localhost:5678"

smoke: ## Verifica que los servicios principales esten vivos
	@echo "Verificando servicios Docker..."
	@docker-compose ps
	@echo ""
	@echo "Probando n8n health..."
	@wget -q --spider http://localhost:5678/healthz 2>/dev/null && echo "n8n OK" || echo "n8n no responde (puede estar arrancando, espera 30s)"

reset-n8n: ## Fuerza reimportacion de workflows en el proximo arranque
	@echo "Eliminando marcador de importacion..."
	docker-compose exec n8n rm -f /home/node/.n8n/.workflows_imported
	@echo "Reiniciando n8n..."
	docker-compose restart n8n
	@echo "n8n reimportara workflows al arrancar"

deploy: ## Despliega los manifiestos en el cluster de Kubernetes activo
	@echo "Desplegando en Kubernetes..."
	kubectl apply -k k8s/overlays/prod/ || kubectl apply -f k8s/base/
	@echo "Despliegue solicitado."

demo09: ## Ejecuta la demostracion del Caso 09
	@echo "Iniciando demo Caso 09 (Python -> FastAPI Gateway)..."
	python3 hub.py ejecutar 09-python-to-gateway
