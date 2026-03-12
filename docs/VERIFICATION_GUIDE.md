# Guía de Verificación del Repositorio

Esta guía detalla los pasos necesarios para asegurar que el entorno de **Social Bot Scheduler** sea correcto, seguro y esté listo para operar.

## 1. Verificación de Salud Local (Diagnóstico)

El primer paso es usar las herramientas de autodiagnóstico integradas en el HUB.

```bash
# Opción A: Usando el Makefile
make doctor

# Opción B: Usando el HUB directamente
python hub.py doctor
```

**¿Qué verifica este comando?**
- Versión de Docker y Docker Compose.
- Validez de los manifiestos YAML de cada caso.
- Estado de los logs de auditoría.
- **Recursos del Host**: Verifica si tienes suficiente RAM y Disco para el stack completo.

## 2. Verificación de Infraestructura

Una vez confirmado el diagnóstico, levanta el stack y verifica que los contenedores estén operativos.

```bash
# Levanta todo el stack (Perfil Full)
make up

# Verifica el estado de los contenedores
docker-compose ps
```

## 3. Verificación de Integración (End-to-End)

Para confirmar que el "circuito" (Chatbot -> n8n -> Dashboard) funciona, tienes dos niveles de prueba:

### A. Prueba Global (Dashboard)
1. Abre [http://localhost:8080](http://localhost:8080) en tu navegador.
2. Observa el indicador de **"Estado del Entorno"**.
3. Haz clic en **"?? PROBAR INTEGRACI?N GLOBAL"**. El Dashboard ejecutar? secuencialmente los 9 casos y mostrar? los resultados en tiempo real.

### B. Prueba Individual (CLI)
Si prefieres la terminal, puedes ejecutar casos específicos:

```bash
# Ejecutar Caso 01 (Modo Simulación por defecto)
python hub.py ejecutar 01-python-to-php

# Ejecutar Caso 01 (Modo Real)
python hub.py ejecutar 01-python-to-php --real
```

## 4. Verificación de Calidad y Seguridad

Si planeas contribuir o validar el cumplimiento de estándares, ejecuta la suite de tests y auditoría:

```bash
# Verificar formato de código
black --check .

# Auditoría de seguridad de dependencias
pip-audit --ignore-vuln CVE-2026-1703

# Tests unitarios y de tipado
mypy cases/01-python-to-php/origin/src/social_bot
pytest cases/01-python-to-php/origin/tests/
```

## 5. Limpieza y Reseteo

Si el sistema presenta comportamientos erráticos, realiza una limpieza profunda:

```bash
make clean
```
esto eliminará volúmenes y redes, permitiendo una reinstalación "desde cero" limpia.


## 6. Verificacion del Caso 09

```bash
make demo09
```

Valida lo siguiente en `http://localhost:8090`:
- autenticacion obligatoria por `X-API-Key` desde n8n
- requests recientes con `request_id`, `action`, `owner`, `limit`, `status`, `http_status`, `latency_ms`, `mode` y `api_key_prefix`
- errores recientes desde DLQ
- top repos por stars leidos desde DuckDB
